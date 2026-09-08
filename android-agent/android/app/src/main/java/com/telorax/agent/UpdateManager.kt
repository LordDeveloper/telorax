package com.telorax.agent

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.core.content.FileProvider
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File

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
