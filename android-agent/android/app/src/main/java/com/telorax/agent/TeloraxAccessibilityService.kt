package com.telorax.agent

import android.accessibilityservice.AccessibilityService
import android.content.ComponentName
import android.content.Context
import android.view.accessibility.AccessibilityEvent
import java.util.concurrent.atomic.AtomicBoolean

class TeloraxAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.packageName?.toString()?.startsWith("org.telegram.messenger") != true) {
            return
        }
        val root = rootInActiveWindow
        if (root != null) {
            canObserveUi.set(true)
            if (event.eventType == AccessibilityEvent.TYPE_VIEW_CLICKED) {
                canPerformActions.set(true)
            }
        }
    }

    override fun onInterrupt() = Unit

    override fun onServiceConnected() {
        super.onServiceConnected()
        serviceConnected.set(true)
    }

    companion object {
        private val serviceConnected = AtomicBoolean(false)
        private val canObserveUi = AtomicBoolean(false)
        private val canPerformActions = AtomicBoolean(false)

        fun isEnabled(context: Context): Boolean {
            val enabled = android.provider.Settings.Secure.getString(
                context.contentResolver,
                android.provider.Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES,
            ) ?: return false
            val target = ComponentName(context, TeloraxAccessibilityService::class.java).flattenToString()
            return enabled.split(':').any { it.equals(target, ignoreCase = true) }
        }

        fun canObserveUi(): Boolean = serviceConnected.get() && canObserveUi.get()

        fun canPerformActions(): Boolean = serviceConnected.get() && canPerformActions.get()
    }
}
