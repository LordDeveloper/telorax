package com.telorax.agent

import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private lateinit var prefs: Prefs
    private lateinit var repository: AgentRepository
    private lateinit var wireGuardBridge: WireGuardBridge
    private lateinit var updateManager: UpdateManager
    private lateinit var statusView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = Prefs(this)
        repository = AgentRepository(this, prefs)
        wireGuardBridge = WireGuardBridge(this)
        updateManager = UpdateManager(this)
        statusView = findViewById(R.id.statusText)

        findViewById<EditText>(R.id.baseUrlInput).setText(prefs.baseUrl)
        findViewById<EditText>(R.id.agentIdInput).setText(prefs.agentId)
        findViewById<EditText>(R.id.agentTokenInput).setText(prefs.agentToken)

        findViewById<Button>(R.id.saveButton).setOnClickListener { saveSettings() }
        findViewById<Button>(R.id.accessibilityButton).setOnClickListener { openAccessibilitySettings() }
        findViewById<Button>(R.id.bootstrapButton).setOnClickListener { bootstrap() }
        findViewById<Button>(R.id.updateButton).setOnClickListener { checkUpdate() }

        lifecycleScope.launch {
            while (isActive) {
                delay(15_000)
                heartbeat()
            }
        }
    }

    private fun saveSettings() {
        prefs.baseUrl = findViewById<EditText>(R.id.baseUrlInput).text.toString().trim()
        prefs.agentId = findViewById<EditText>(R.id.agentIdInput).text.toString().trim()
        prefs.agentToken = findViewById<EditText>(R.id.agentTokenInput).text.toString().trim()
        appendStatus("settings saved")
    }

    private fun openAccessibilitySettings() {
        startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
    }

    private fun bootstrap() {
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
            }.onFailure {
                appendStatus("bootstrap failed: ${it.message}")
            }
        }
    }

    private fun heartbeat() {
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.IO) {
                    val caps = CapabilityProbe.collect(this@MainActivity)
                    repository.heartbeat("online", caps, tunnelUp = false)
                }
            }.onSuccess {
                appendStatus("heartbeat ok")
            }
        }
    }

    private fun checkUpdate() {
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.IO) {
                    val update = repository.checkUpdate()
                    updateManager.maybeInstall(update)
                }
            }.onSuccess {
                appendStatus(it)
            }.onFailure {
                appendStatus("update failed: ${it.message}")
            }
        }
    }

    private fun appendStatus(message: String) {
        statusView.append("\n$message")
    }
}
