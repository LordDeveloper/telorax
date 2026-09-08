package tunnel

import (
	"strings"
	"testing"

	"github.com/LordDeveloper/telorax/android-agent/internal/api"
)

func TestBuildClientConfig(t *testing.T) {
	text := BuildClientConfig(api.WireGuardConfig{
		ClientAddress:   "10.8.0.22/32",
		ServerPublicKey: "SERVER_PUBLIC_KEY",
		Endpoint:        "vpn.example.com:51820",
	})
	if !strings.Contains(text, "Address = 10.8.0.22/32") {
		t.Fatalf("unexpected config: %s", text)
	}
	if !strings.Contains(text, "Endpoint = vpn.example.com:51820") {
		t.Fatalf("missing endpoint: %s", text)
	}
}

func TestApplyDisabled(t *testing.T) {
	manager := NewManager()
	message, err := manager.Apply(api.WireGuardConfig{Enabled: false})
	if err != nil {
		t.Fatalf("apply failed: %v", err)
	}
	if manager.Active() {
		t.Fatal("expected inactive tunnel")
	}
	if message == "" {
		t.Fatal("expected message")
	}
}
