package com.telorax.agent

import android.content.Context
import org.json.JSONObject

class WireGuardBridge(context: Context) {
    private val amneziaBridge = AmneziaBridge(context)

    fun apply(config: JSONObject): String = amneziaBridge.importFromServer(config)
}
