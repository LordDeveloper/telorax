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
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class ProvisioningWorker : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var loopJob: Job? = null
    private val client = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        createChannel()
        startForeground(NOTIFICATION_ID, buildNotification("Waiting for Telegram automation"))
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        loopJob?.cancel()
        loopJob = scope.launch {
            val prefs = Prefs(this@ProvisioningWorker)
            while (isActive) {
                if (prefs.agentToken.isBlank()) {
                    updateNotification("Configure agent token first")
                    delay(5_000)
                    continue
                }
                if (!CapabilityProbe.collect(this@ProvisioningWorker).optBoolean("can_perform_actions")) {
                    updateNotification("Enable Telegram accessibility service")
                    delay(5_000)
                    continue
                }
                runCatching {
                    claimJob(prefs)
                }.onSuccess { message ->
                    updateNotification(message)
                }.onFailure {
                    updateNotification("claim failed: ${it.message}")
                }
                delay(5_000)
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        loopJob?.cancel()
        scope.cancel()
        super.onDestroy()
    }

    private fun claimJob(prefs: Prefs): String {
        val payload = JSONObject().put("provider", "android-agent")
        val request = Request.Builder()
            .url("${prefs.effectiveBaseUrl(this@ProvisioningWorker)}/v1/provisioning/agent/claim")
            .addHeader("Content-Type", "application/json")
            .addHeader("X-Telorax-Agent-Id", prefs.agentId)
            .addHeader("X-Telorax-Agent-Token", prefs.agentToken)
            .post(payload.toString().toRequestBody(JSON))
            .build()
        client.newCall(request).execute().use { response ->
            if (response.code == 204) {
                return "No provisioning jobs in queue"
            }
            if (!response.isSuccessful) {
                throw IllegalStateException("HTTP ${response.code}")
            }
            val body = response.body?.string().orEmpty()
            val job = JSONObject(body)
            return "Claimed job #${job.optInt("id")} for +${job.optLong("msisdn")}"
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
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    private fun buildNotification(text: String): Notification =
        NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_download_done)
            .setContentTitle("Telorax Agent")
            .setContentText(text)
            .setOngoing(true)
            .build()

    private fun updateNotification(text: String) {
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, buildNotification(text))
    }

    companion object {
        private const val CHANNEL_ID = "telorax_provisioning"
        private const val NOTIFICATION_ID = 42
        private val JSON = "application/json; charset=utf-8".toMediaType()

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
