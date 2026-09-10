package com.telorax.agent

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityNodeInfo
import kotlinx.coroutines.delay

data class SignupJob(
    val id: Int,
    val msisdn: Long,
    val firstName: String,
    val lastName: String,
)

object TelegramUiAutomator {
    private val startLabels = listOf("Start Messaging", "Start messaging", "شروع پیام‌رسانی")
    private val continueLabels = listOf("Continue", "ادامه")
    private val nextLabels = listOf("Next", "بعدی", "Done", "تمام")

    suspend fun runSignup(service: AccessibilityService, job: SignupJob, smsCodeProvider: suspend () -> String) {
        launchTelegram(service)
        delay(1500)
        waitAndTap(service, startLabels)
        delay(800)
        waitAndTap(service, continueLabels)
        delay(800)
        setPhoneNumber(service, "+${job.msisdn}")
        delay(500)
        waitAndTap(service, nextLabels)
        delay(1500)
        val smsCode = smsCodeProvider()
        enterVerificationCode(service, smsCode)
        delay(1200)
        enterName(service, job.firstName, job.lastName)
        delay(500)
        waitAndTap(service, nextLabels + listOf("Done", "Sign up"))
    }

    private suspend fun waitAndTap(service: AccessibilityService, labels: List<String>, attempts: Int = 20) {
        repeat(attempts) {
            if (tapAny(service, labels)) {
                return
            }
            delay(500)
        }
        throw IllegalStateException("UI control not found: ${labels.first()}")
    }

    private fun launchTelegram(service: AccessibilityService) {
        val launch = service.packageManager.getLaunchIntentForPackage("org.telegram.messenger")
            ?: throw IllegalStateException("Telegram is not installed")
        launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        service.startActivity(launch)
    }

    private fun tapAny(service: AccessibilityService, labels: List<String>): Boolean {
        for (label in labels) {
            if (tapByText(service, label)) {
                return true
            }
        }
        return false
    }

    private fun tapByText(service: AccessibilityService, text: String): Boolean {
        val root = service.rootInActiveWindow ?: return false
        val node = root.findByText(text) ?: return false
        return node.clickSelfOrParent()
    }

    private fun setPhoneNumber(service: AccessibilityService, phone: String) {
        val root = service.rootInActiveWindow ?: throw IllegalStateException("Telegram UI not ready")
        val field = root.findFirstEditText() ?: throw IllegalStateException("Phone field not found")
        if (!field.setNodeText(phone)) {
            throw IllegalStateException("Unable to enter phone number")
        }
    }

    private fun enterVerificationCode(service: AccessibilityService, code: String) {
        val root = service.rootInActiveWindow ?: throw IllegalStateException("Code screen not ready")
        val fields = root.findAllEditTexts()
        if (fields.isEmpty()) {
            throw IllegalStateException("Code field not found")
        }
        if (fields.size == 1) {
            if (!fields[0].setNodeText(code)) {
                throw IllegalStateException("Unable to enter verification code")
            }
            return
        }
        code.forEachIndexed { index, char ->
            if (index >= fields.size) {
                return@forEachIndexed
            }
            fields[index].setNodeText(char.toString())
        }
    }

    private fun enterName(service: AccessibilityService, firstName: String, lastName: String) {
        val root = service.rootInActiveWindow ?: throw IllegalStateException("Name screen not ready")
        val fields = root.findAllEditTexts()
        if (fields.isEmpty()) {
            throw IllegalStateException("Name fields not found")
        }
        fields[0].setNodeText(firstName)
        if (fields.size > 1) {
            fields[1].setNodeText(lastName)
        }
    }

    private fun AccessibilityNodeInfo.findByText(search: String): AccessibilityNodeInfo? {
        val label = text?.toString().orEmpty()
        if (label.equals(search, ignoreCase = true) || contentDescription?.contains(search, true) == true) {
            return this
        }
        for (index in 0 until childCount) {
            val child = getChild(index) ?: continue
            val found = child.findByText(search)
            if (found != null) {
                return found
            }
        }
        return null
    }

    private fun AccessibilityNodeInfo.findFirstEditText(): AccessibilityNodeInfo? {
        if (className?.contains("EditText") == true) {
            return this
        }
        for (index in 0 until childCount) {
            val child = getChild(index) ?: continue
            val found = child.findFirstEditText()
            if (found != null) {
                return found
            }
        }
        return null
    }

    private fun AccessibilityNodeInfo.findAllEditTexts(): List<AccessibilityNodeInfo> {
        val items = mutableListOf<AccessibilityNodeInfo>()
        collectEditTexts(items)
        return items
    }

    private fun AccessibilityNodeInfo.collectEditTexts(out: MutableList<AccessibilityNodeInfo>) {
        if (className?.contains("EditText") == true) {
            out.add(this)
        }
        for (index in 0 until childCount) {
            getChild(index)?.collectEditTexts(out)
        }
    }

    private fun AccessibilityNodeInfo.setNodeText(value: String): Boolean {
        val args = Bundle()
        args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, value)
        if (performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)) {
            return true
        }
        if (performAction(AccessibilityNodeInfo.ACTION_FOCUS)) {
            return performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        }
        return false
    }

    private fun AccessibilityNodeInfo.clickSelfOrParent(): Boolean {
        var current: AccessibilityNodeInfo? = this
        while (current != null) {
            if (current.isClickable && current.performAction(AccessibilityNodeInfo.ACTION_CLICK)) {
                return true
            }
            current = current.parent
        }
        return performAction(AccessibilityNodeInfo.ACTION_CLICK)
    }
}
