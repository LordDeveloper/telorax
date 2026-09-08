package com.telorax.agent

import android.Manifest
import android.content.ClipboardManager
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.widget.doAfterTextChanged
import androidx.lifecycle.lifecycleScope
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private lateinit var prefs: Prefs
    private lateinit var repository: AgentRepository
    private lateinit var amneziaBridge: AmneziaBridge
    private lateinit var wireGuardBridge: WireGuardBridge
    private lateinit var updateManager: UpdateManager

    private lateinit var vpnStatusText: TextView
    private lateinit var serverStatusText: TextView
    private lateinit var telegramStatusText: TextView
    private lateinit var profileStatusText: TextView
    private lateinit var statusView: TextView
    private lateinit var provisioningButton: MaterialButton

    private val importFileLauncher = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) {
            importConfigFromUri(uri)
        }
    }

    private val notificationPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = Prefs(this)
        repository = AgentRepository(this, prefs)
        amneziaBridge = AmneziaBridge(this)
        wireGuardBridge = WireGuardBridge(this)
        updateManager = UpdateManager(this)

        bindViews()
        loadSettings()
        bindActions()
        requestNotificationPermission()
        refreshStatusCards()

        lifecycleScope.launch {
            while (isActive) {
                delay(5_000)
                refreshStatusCards()
                heartbeatIfReady()
            }
        }
    }

    override fun onResume() {
        super.onResume()
        refreshStatusCards()
    }

    private fun bindViews() {
        vpnStatusText = findViewById(R.id.vpnStatusText)
        serverStatusText = findViewById(R.id.serverStatusText)
        telegramStatusText = findViewById(R.id.telegramStatusText)
        profileStatusText = findViewById(R.id.profileStatusText)
        statusView = findViewById(R.id.statusText)
        provisioningButton = findViewById(R.id.provisioningButton)
    }

    private fun loadSettings() {
        findViewById<TextInputEditText>(R.id.publicUrlInput).setText(prefs.publicBaseUrl)
        findViewById<TextInputEditText>(R.id.vpnUrlInput).setText(prefs.vpnBaseUrl)
        findViewById<TextInputEditText>(R.id.agentIdInput).setText(prefs.agentId)
        findViewById<TextInputEditText>(R.id.agentTokenInput).setText(prefs.agentToken)
        updateProvisioningButton()
    }

    private fun bindActions() {
        findViewById<MaterialButton>(R.id.importFileButton).setOnClickListener {
            importFileLauncher.launch(arrayOf("*/*"))
        }
        findViewById<MaterialButton>(R.id.importClipboardButton).setOnClickListener {
            importFromClipboard()
        }
        findViewById<MaterialButton>(R.id.openAmneziaButton).setOnClickListener {
            openAmneziaApp()
        }
        findViewById<MaterialButton>(R.id.saveButton).setOnClickListener { saveSettings() }
        findViewById<MaterialButton>(R.id.bootstrapButton).setOnClickListener { bootstrap() }
        findViewById<MaterialButton>(R.id.accessibilityButton).setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }
        findViewById<MaterialButton>(R.id.openTelegramButton).setOnClickListener {
            TelegramProbe.openApp(this)
        }
        provisioningButton.setOnClickListener { toggleProvisioning() }
        findViewById<MaterialButton>(R.id.updateButton).setOnClickListener { checkUpdate() }

        listOf(R.id.publicUrlInput, R.id.vpnUrlInput, R.id.agentIdInput, R.id.agentTokenInput).forEach { id ->
            findViewById<TextInputEditText>(id).doAfterTextChanged { refreshStatusCards() }
        }
    }

    private fun saveSettings() {
        prefs.publicBaseUrl = findViewById<TextInputEditText>(R.id.publicUrlInput).text.toString().trim()
        prefs.vpnBaseUrl = findViewById<TextInputEditText>(R.id.vpnUrlInput).text.toString().trim()
        prefs.agentId = findViewById<TextInputEditText>(R.id.agentIdInput).text.toString().trim()
        prefs.agentToken = findViewById<TextInputEditText>(R.id.agentTokenInput).text.toString().trim()
        appendStatus("credentials saved")
        refreshStatusCards()
    }

    private fun importConfigFromUri(uri: Uri) {
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.IO) {
                    val text = contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
                        ?: throw IllegalStateException("empty config file")
                    val config = AmneziaConfigParser.parse(text)
                    amneziaBridge.importConfig(config)
                }
            }.onSuccess { message ->
                appendStatus(message)
                refreshStatusCards()
            }.onFailure {
                appendStatus("import failed: ${it.message}")
            }
        }
    }

    private fun importFromClipboard() {
        val clipboard = getSystemService(ClipboardManager::class.java)
        val clip = clipboard.primaryClip
        if (clip == null || clip.itemCount == 0) {
            appendStatus("clipboard is empty")
            return
        }
        val text = clip.getItemAt(0).coerceToText(this).toString()
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.Default) {
                    val config = AmneziaConfigParser.parse(text)
                    amneziaBridge.importConfig(config)
                }
            }.onSuccess { message ->
                appendStatus(message)
                refreshStatusCards()
            }.onFailure {
                appendStatus("clipboard import failed: ${it.message}")
            }
        }
    }

    private fun openAmneziaApp() {
        val packages = listOf("org.amnezia.vpn", "net.amnezia.vpn")
        for (packageName in packages) {
            val launch = packageManager.getLaunchIntentForPackage(packageName)
            if (launch != null) {
                startActivity(launch)
                appendStatus("opened $packageName")
                return
            }
        }
        appendStatus("Amnezia VPN is not installed")
    }

    private fun bootstrap() {
        saveSettings()
        if (prefs.agentToken.isBlank()) {
            appendStatus("set agent token first")
            return
        }
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.IO) {
                    val caps = CapabilityProbe.collect(this@MainActivity)
                    val registered = repository.bootstrap(caps)
                    val config = repository.fetchConfig()
                    val tunnelMessage = wireGuardBridge.apply(config.getJSONObject("wireguard"))
                    Pair(registered, tunnelMessage)
                }
            }.onSuccess { (registered, tunnelMessage) ->
                appendStatus("registered: ${registered.optString("device_id")}")
                appendStatus(tunnelMessage)
                serverStatusText.text = getString(R.string.status_server_ok)
                serverStatusText.setTextColor(getColor(R.color.success))
            }.onFailure {
                appendStatus("bootstrap failed: ${it.message}")
            }
        }
    }

    private fun heartbeatIfReady() {
        if (prefs.agentToken.isBlank()) {
            return
        }
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.IO) {
                    val caps = CapabilityProbe.collect(this@MainActivity)
                    repository.heartbeat(
                        status = "online",
                        capabilities = caps,
                        tunnelUp = VpnStatusMonitor.isVpnActive(this@MainActivity),
                    )
                }
            }.onSuccess {
                serverStatusText.text = getString(R.string.status_server_ok)
                serverStatusText.setTextColor(getColor(R.color.success))
            }
        }
    }

    private fun toggleProvisioning() {
        if (prefs.provisioningEnabled) {
            prefs.provisioningEnabled = false
            ProvisioningWorker.stop(this)
            appendStatus("provisioning worker stopped")
        } else {
            saveSettings()
            prefs.provisioningEnabled = true
            ProvisioningWorker.start(this)
            appendStatus("provisioning worker started")
        }
        updateProvisioningButton()
    }

    private fun updateProvisioningButton() {
        provisioningButton.text = if (prefs.provisioningEnabled) {
            getString(R.string.stop_provisioning)
        } else {
            getString(R.string.start_provisioning)
        }
    }

    private fun checkUpdate() {
        if (prefs.agentToken.isBlank()) {
            appendStatus("save agent token before checking updates")
            return
        }
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.IO) {
                    val update = repository.checkUpdate()
                    updateManager.maybeInstall(update)
                }
            }.onSuccess { appendStatus(it) }
                .onFailure { appendStatus("update failed: ${it.message}") }
        }
    }

    private fun refreshStatusCards() {
        val vpnUp = VpnStatusMonitor.isVpnActive(this)
        vpnStatusText.text = if (vpnUp) {
            getString(R.string.status_vpn_on)
        } else {
            getString(R.string.status_vpn_off)
        }
        vpnStatusText.setTextColor(getColor(if (vpnUp) R.color.success else R.color.warning))

        profileStatusText.text = if (prefs.amneziaProfileName.isBlank()) {
            getString(R.string.status_profile_none)
        } else {
            "Amnezia profile: ${prefs.amneziaProfileName}"
        }

        val caps = CapabilityProbe.collect(this)
        telegramStatusText.text = when {
            !TelegramProbe.isInstalled(this) -> getString(R.string.status_telegram_missing)
            caps.optBoolean("can_perform_actions") -> getString(R.string.status_telegram_ready)
            else -> getString(R.string.status_telegram_unknown)
        }
        telegramStatusText.setTextColor(
            getColor(
                if (caps.optBoolean("can_perform_actions")) R.color.success else R.color.text_secondary,
            ),
        )
    }

    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            return
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
            != PackageManager.PERMISSION_GRANTED
        ) {
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    private fun appendStatus(message: String) {
        statusView.append("\n$message")
    }
}
