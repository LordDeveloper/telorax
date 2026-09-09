package com.telorax.agent

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

class ProvisioningWorker : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var loopJob: Job? = null
    private var activeJobId: Int? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        createChannel()
        startForeground(NOTIFICATION_ID, buildNotification("Waiting for provisioning jobs"))
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        loopJob?.cancel()
        loopJob = scope.launch {
            val prefs = Prefs(this@ProvisioningWorker)
            val api = AgentApiClient(this@ProvisioningWorker, prefs)
            val orchestrator = SignupOrchestrator(api)
            while (isActive) {
                if (prefs.agentToken.isBlank()) {
                    updateNotification("Configure agent token first")
                    delay(5_000)
                    continue
                }
                if (!TeloraxAccessibilityService.isEnabled(this@ProvisioningWorker)) {
                    updateNotification("Enable Telorax accessibility service")
                    delay(5_000)
                    continue
                }
                if (!VpnStatusMonitor.isVpnActive(this@ProvisioningWorker)) {
                    updateNotification("Connect Amnezia VPN first")
                    delay(5_000)
                    continue
                }
                if (activeJobId != null) {
                    delay(2_000)
                    continue
                }
                runCatching {
                    processNextJob(api, orchestrator)
                }.onSuccess { message ->
                    updateNotification(message)
                }.onFailure {
                    updateNotification(it.message ?: "provisioning failed")
                }
                delay(3_000)
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        loopJob?.cancel()
        scope.cancel()
        super.onDestroy()
    }

    private suspend fun processNextJob(api: AgentApiClient, orchestrator: SignupOrchestrator): String {
        val claimed = withContext(Dispatchers.IO) { api.claimJob() } ?: return "No provisioning jobs in queue"
        val jobId = claimed.getInt("id")
        activeJobId = jobId
        updateNotification("Running Telegram signup for job #$jobId")
        return try {
            orchestrator.runClaimedJob(claimed)
        } catch (error: Exception) {
            withContext(Dispatchers.IO) {
                api.failJob(jobId, error.message ?: "Signup automation failed")
            }
            throw error
        } finally {
            activeJobId = null
        }
    }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return
        }
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Telorax provisioning",
            NotificationManager.IMPORTANCE_LOW,
        )
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    private fun buildNotification(text: String): Notification =
        NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_download_done)
            .setContentTitle("Telorax Agent")
            .setContentText(text)
            .setOngoing(true)
            .build()

    private fun updateNotification(text: String) {
        getSystemService(NotificationManager::class.java)
            .notify(NOTIFICATION_ID, buildNotification(text))
    }

    companion object {
        private const val CHANNEL_ID = "telorax_provisioning"
        private const val NOTIFICATION_ID = 42

        fun start(context: Context) {
            val intent = Intent(context, ProvisioningWorker::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, ProvisioningWorker::class.java))
        }
    }
}
