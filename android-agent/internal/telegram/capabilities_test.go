package telegram

import "testing"

func TestEvaluateReady(t *testing.T) {
	caps := Evaluate(true, true, true, true, "")
	if !caps.ReadyForAutomation() {
		t.Fatal("expected ready")
	}
}

func TestEvaluateMissingAccessibility(t *testing.T) {
	caps := Evaluate(false, true, false, false, "")
	if caps.ReadyForAutomation() {
		t.Fatal("expected not ready")
	}
	if caps.Notes == "" {
		t.Fatal("expected note")
	}
}
