package com.telorax.agent

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.core.content.FileProvider
import org.json.JSONObject
import java.io.File

class AmneziaBridge(private val context: Context) {
    private val amneziaPackages = listOf(
        "org.amnezia.vpn",
        "net.amnezia.vpn",
    )

    fun importConfig(config: AmneziaConfig): String {
        prefs(context).amneziaProfileName = config.profileName
        prefs(context).amneziaConfigRaw = config.rawJson
        config.apiEndpoint?.let { endpoint ->
            if (prefs(context).publicBaseUrl.isBlank()) {
                prefs(context).publicBaseUrl = endpoint.trimEnd('/')
            }
        }
        return launchImport(config.rawJson, "${config.profileName}.vpn")
    }

    fun importFromServer(config: JSONObject): String {
        if (!config.optBoolean("enabled", false)) {
            return "server tunnel disabled"
        }
        val text = config.optString("config_text")
        if (text.isBlank()) {
            return "server tunnel config missing"
        }
        return launchImport(text, "telorax-server.conf")
    }

    fun isAmneziaInstalled(): Boolean =
        amneziaPackages.any { packageName ->
            runCatching {
                context.packageManager.getPackageInfo(packageName, 0)
                true
            }.getOrDefault(false)
        }

    private fun launchImport(content: String, fileName: String): String {
        val cacheFile = File(context.cacheDir, fileName)
        cacheFile.writeText(content)
        val uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            cacheFile,
        )

        for (packageName in amneziaPackages) {
            if (!isPackageInstalled(packageName)) {
                continue
            }
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/octet-stream")
                setPackage(packageName)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            return try {
                context.startActivity(intent)
                "opened Amnezia import for $packageName"
            } catch (_: Exception) {
                continue
            }
        }

        val shareIntent = Intent(Intent.ACTION_SEND).apply {
            type = "application/octet-stream"
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_TEXT, content)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        return try {
            context.startActivity(
                Intent.createChooser(shareIntent, "Import VPN config").apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                },
            )
            "share sheet opened — choose Amnezia VPN"
        } catch (_: Exception) {
            "install Amnezia VPN from https://amnezia.org and retry"
        }
    }

    private fun isPackageInstalled(packageName: String): Boolean =
        runCatching {
            context.packageManager.getPackageInfo(packageName, 0)
            true
        }.getOrDefault(false)

    private fun prefs(context: Context): Prefs = Prefs(context)
}
