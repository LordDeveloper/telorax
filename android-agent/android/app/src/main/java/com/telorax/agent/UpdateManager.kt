package com.telorax.agent

import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.net.Uri
import android.os.Build
import androidx.core.content.FileProvider
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.FileInputStream

class UpdateManager(private val context: Context) {
    private val client = OkHttpClient()

    fun maybeInstall(update: org.json.JSONObject): String {
        if (!update.optBoolean("update_available", false)) {
            return "no update"
        }
        val url = update.optString("url")
        if (url.isBlank()) {
            return "update url missing"
        }
        val request = Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                return "download failed"
            }
            val bytes = response.body?.bytes() ?: return "empty update"
            val apk = File(context.cacheDir, "telorax-agent-update.apk")
            apk.writeBytes(bytes)
            installApk(apk)
            return "update install started"
        }
    }

    private fun installApk(apk: File) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            runCatching { installWithSession(apk) }
                .onFailure { installWithIntent(apk) }
            return
        }
        installWithIntent(apk)
    }

    private fun installWithSession(apk: File) {
        val installer = context.packageManager.packageInstaller
        val params = PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL).apply {
            setAppPackageName(context.packageName)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                setRequireUserAction(PackageInstaller.SessionParams.USER_ACTION_REQUIRED)
            }
        }
        val sessionId = installer.createSession(params)
        val session = installer.openSession(sessionId)
        session.use { activeSession ->
            FileInputStream(apk).use { input ->
                activeSession.openWrite("telorax-agent-update", 0, apk.length()).use { output ->
                    input.copyTo(output)
                    activeSession.fsync(output)
                }
            }
            val intent = Intent(context, UpdateInstallReceiver::class.java)
            val flags = PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            val pendingIntent = PendingIntent.getBroadcast(context, sessionId, intent, flags)
            activeSession.commit(pendingIntent.intentSender)
        }
    }

    private fun installWithIntent(apk: File) {
        val uri: Uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            apk,
        )
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(intent)
    }
}

class UpdateInstallReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) = Unit
}
