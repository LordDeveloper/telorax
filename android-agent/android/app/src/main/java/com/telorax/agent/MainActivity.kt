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
import androidx.appcompat.app.AlertDialog
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
    private lateinit var setupHintText: TextView
    private lateinit var step1Badge: TextView
    private lateinit var step2Badge: TextView
    private lateinit var step3Badge: TextView
    private lateinit var provisioningButton: MaterialButton
    private var serverOnline = false

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
        maybeShowInstallHelp()
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
        setupHintText = findViewById(R.id.setupHintText)
        step1Badge = findViewById(R.id.step1Badge)
        step2Badge = findViewById(R.id.step2Badge)
        step3Badge = findViewById(R.id.step3Badge)
        provisioningButton = findViewById(R.id.provisioningButton)
        findViewById<TextView>(R.id.versionText).text =
            getString(R.string.version_label, BuildConfig.VERSION_NAME)
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
        findViewById<MaterialButton>(R.id.clearLogButton).setOnClickListener {
            statusView.text = getString(R.string.log_placeholder)
        }

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
                serverOnline = true
                applyStatusChip(serverStatusText, getString(R.string.status_server_ok), StatusTone.SUCCESS)
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
                serverOnline = true
                applyStatusChip(serverStatusText, getString(R.string.status_server_ok), StatusTone.SUCCESS)
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
        if (prefs.provisioningEnabled) {
            provisioningButton.text = getString(R.string.stop_provisioning)
            provisioningButton.backgroundTintList =
                ContextCompat.getColorStateList(this, R.color.danger)
        } else {
            provisioningButton.text = getString(R.string.start_provisioning)
            provisioningButton.backgroundTintList =
                ContextCompat.getColorStateList(this, R.color.success)
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
        applyStatusChip(
            vpnStatusText,
            if (vpnUp) getString(R.string.status_vpn_on) else getString(R.string.status_vpn_off),
            if (vpnUp) StatusTone.SUCCESS else StatusTone.WARNING,
        )

        profileStatusText.text = if (prefs.amneziaProfileName.isBlank()) {
            getString(R.string.status_profile_none)
        } else {
            "Amnezia profile: ${prefs.amneziaProfileName}"
        }

        val caps = CapabilityProbe.collect(this)
        val telegramReady = TelegramProbe.isInstalled(this) && caps.optBoolean("can_perform_actions")
        when {
            !TelegramProbe.isInstalled(this) -> {
                applyStatusChip(
                    telegramStatusText,
                    getString(R.string.status_telegram_missing),
                    StatusTone.DANGER,
                )
            }
            telegramReady -> {
                applyStatusChip(
                    telegramStatusText,
                    getString(R.string.status_telegram_ready),
                    StatusTone.SUCCESS,
                )
            }
            else -> {
                applyStatusChip(
                    telegramStatusText,
                    getString(R.string.status_telegram_unknown),
                    StatusTone.NEUTRAL,
                )
            }
        }

        val serverReady = prefs.agentToken.isNotBlank() && serverOnline
        if (!serverReady) {
            applyStatusChip(
                serverStatusText,
                getString(R.string.status_server_unknown),
                StatusTone.NEUTRAL,
            )
        } else {
            applyStatusChip(
                serverStatusText,
                getString(R.string.status_server_ok),
                StatusTone.SUCCESS,
            )
        }

        updateSetupProgress(vpnUp, serverReady, telegramReady)
    }

    private fun updateSetupProgress(vpnUp: Boolean, serverReady: Boolean, telegramReady: Boolean) {
        val profileReady = prefs.amneziaProfileName.isNotBlank()
        val step1Done = profileReady || vpnUp
        val step2Done = serverReady
        val step3Done = telegramReady && prefs.provisioningEnabled

        styleStepBadge(step1Badge, 1, step1Done, !step1Done && !step2Done && !step3Done)
        styleStepBadge(step2Badge, 2, step2Done, step1Done && !step2Done)
        styleStepBadge(step3Badge, 3, step3Done, step2Done && !step3Done)

        setupHintText.text = when {
            step3Done -> getString(R.string.setup_hint_done)
            step2Done -> getString(R.string.setup_hint_telegram)
            step1Done -> getString(R.string.setup_hint_server)
            else -> getString(R.string.setup_hint_vpn)
        }
    }

    private fun styleStepBadge(badge: TextView, step: Int, done: Boolean, active: Boolean) {
        badge.text = if (done) "✓" else step.toString()
        badge.setBackgroundResource(
            when {
                done -> R.drawable.bg_step_done
                active -> R.drawable.bg_step_active
                else -> R.drawable.bg_step_pending
            },
        )
        badge.setTextColor(
            getColor(
                when {
                    done || active -> R.color.on_primary
                    else -> R.color.text_secondary
                },
            ),
        )
    }

    private fun applyStatusChip(view: TextView, label: String, tone: StatusTone) {
        view.text = label
        view.setBackgroundResource(
            when (tone) {
                StatusTone.SUCCESS -> R.drawable.bg_status_success
                StatusTone.WARNING -> R.drawable.bg_status_warning
                StatusTone.DANGER -> R.drawable.bg_status_danger
                StatusTone.NEUTRAL -> R.drawable.bg_status_neutral
            },
        )
        view.setTextColor(
            getColor(
                when (tone) {
                    StatusTone.SUCCESS -> R.color.success
                    StatusTone.WARNING -> R.color.warning
                    StatusTone.DANGER -> R.color.danger
                    StatusTone.NEUTRAL -> R.color.text_secondary
                },
            ),
        )
    }

    private fun maybeShowInstallHelp() {
        if (prefs.installHelpShown) {
            return
        }
        prefs.installHelpShown = true
        AlertDialog.Builder(this)
            .setTitle(R.string.install_blocked_title)
            .setMessage(R.string.install_blocked_message)
            .setPositiveButton(android.R.string.ok, null)
            .show()
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
        if (statusView.text == getString(R.string.log_placeholder)) {
            statusView.text = message
        } else {
            statusView.append("\n$message")
        }
    }

    private enum class StatusTone {
        SUCCESS,
        WARNING,
        DANGER,
        NEUTRAL,
    }
}
