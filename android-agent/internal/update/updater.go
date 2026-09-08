package update

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"

	"github.com/LordDeveloper/telorax/android-agent/internal/api"
)

type Result struct {
	Available bool
	Version   string
	URL       string
	SHA256    string
	Mandatory bool
	Notes     string
	Payload   []byte
}

type Manager struct {
	client *api.Client
}

func NewManager(client *api.Client) *Manager {
	return &Manager{client: client}
}

func (m *Manager) Check(ctx context.Context, currentVersion string) (Result, error) {
	resp, err := m.client.CheckUpdate(ctx, currentVersion)
	if err != nil {
		return Result{}, err
	}
	return Result{
		Available: resp.UpdateAvailable,
		Version:   resp.Version,
		URL:       resp.URL,
		SHA256:    resp.SHA256,
		Mandatory: resp.Mandatory,
		Notes:     resp.ReleaseNotes,
	}, nil
}

func (m *Manager) Download(ctx context.Context, result Result) (Result, error) {
	if !result.Available || result.URL == "" {
		return result, nil
	}
	payload, err := m.client.Download(ctx, result.URL)
	if err != nil {
		return Result{}, err
	}
	if result.SHA256 != "" {
		sum := sha256.Sum256(payload)
		if hex.EncodeToString(sum[:]) != result.SHA256 {
			return Result{}, fmt.Errorf("update checksum mismatch")
		}
	}
	result.Payload = payload
	return result, nil
}
