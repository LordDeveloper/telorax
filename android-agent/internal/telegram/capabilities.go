package telegram

import "github.com/LordDeveloper/telorax/android-agent/internal/api"

const OfficialPackage = "org.telegram.messenger"

type Capabilities struct {
	AccessibilityEnabled bool
	CanObserveUI         bool
	CanPerformActions    bool
	PackageInstalled     bool
	Notes                string
}

func (c Capabilities) ReadyForAutomation() bool {
	return c.PackageInstalled && c.AccessibilityEnabled && c.CanObserveUI && c.CanPerformActions
}

func (c Capabilities) ToAPI() api.TelegramCapabilities {
	return api.TelegramCapabilities{
		AccessibilityEnabled: c.AccessibilityEnabled,
		CanObserveUI:         c.CanObserveUI,
		CanPerformActions:    c.CanPerformActions,
		PackageInstalled:     c.PackageInstalled,
		Notes:                c.Notes,
	}
}

func Evaluate(accessibilityEnabled, packageInstalled, canObserve, canPerform bool, notes string) Capabilities {
	if notes == "" {
		switch {
		case !packageInstalled:
			notes = "official Telegram app is not installed"
		case !accessibilityEnabled:
			notes = "accessibility service must be enabled for headless UI control"
		case !canObserve:
			notes = "cannot observe Telegram UI tree yet"
		case !canPerform:
			notes = "cannot perform actions on Telegram UI yet"
		default:
			notes = "telegram automation prerequisites satisfied"
		}
	}
	return Capabilities{
		AccessibilityEnabled: accessibilityEnabled,
		PackageInstalled:     packageInstalled,
		CanObserveUI:         canObserve,
		CanPerformActions:    canPerform,
		Notes:                notes,
	}
}
