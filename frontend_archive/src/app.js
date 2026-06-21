// UI Elements & State
let simulationData = null;
let currentSettings = {
  provider: 'mock',
  apiKey: '',
  model: '',
  githubToken: '',
  githubRepo: 'UedaKazuki-Plainliving/AI-Clone',
  githubBranch: 'main'
};

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSettings();
  initSimulation();
  initReviewer();
  initGitHubCommit();
  initPresets();
  
  // Load settings on startup
  fetchSettings();
});

// 1. Navigation Controller (SPA Router)
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('.content-section');
  const pageTitle = document.getElementById('page-title');

  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Remove active class from all nav items
      navItems.forEach(nav => nav.classList.remove('active'));
      // Add active class to clicked nav item
      item.classList.add('active');

      // Hide all sections
      sections.forEach(sec => sec.classList.remove('active'));
      
      // Show target section
      const targetId = item.getAttribute('href').substring(1);
      const targetSec = document.getElementById(`sec-${targetId}`);
      if (targetSec) {
        targetSec.classList.add('active');
        // Add fade-in animation
        targetSec.classList.add('fade-in');
        setTimeout(() => targetSec.classList.remove('fade-in'), 500);
      }

      // Update Header title
      pageTitle.textContent = item.textContent.trim();
    });
  });
}

// 2. Settings Management
function initSettings() {
  const form = document.getElementById('form-settings');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const settingsData = {
      provider: document.getElementById('setting-provider').value,
      model: document.getElementById('setting-model').value,
      apiKey: document.getElementById('setting-apikey').value,
      githubToken: document.getElementById('setting-ghtoken').value,
      githubRepo: document.getElementById('setting-ghrepo').value,
      githubBranch: document.getElementById('setting-ghbranch').value
    };

    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settingsData)
      });
      
      const res = await response.json();
      if (response.ok) {
        showToast(res.message);
        fetchSettings(); // Refresh UI state
      } else {
        alert('設定の保存に失敗しました: ' + res.detail);
      }
    } catch (err) {
      alert('エラーが発生しました: ' + err.message);
    }
  });
}

async function fetchSettings() {
  try {
    const response = await fetch('/api/settings');
    if (response.ok) {
      const data = await response.json();
      currentSettings = data;
      const provider = data.provider || 'mock';
      
      // Pre-fill form inputs
      document.getElementById('setting-provider').value = provider;
      document.getElementById('setting-model').value = data.model || '';
      document.getElementById('setting-apikey').value = data.apiKey || '';
      document.getElementById('setting-ghtoken').value = data.githubToken || '';
      document.getElementById('setting-ghrepo').value = data.githubRepo || '';
      document.getElementById('setting-ghbranch').value = data.githubBranch || 'main';

      // Update header badge
      const badge = document.getElementById('mode-badge');
      if (provider === 'mock') {
        badge.textContent = 'Mock 実行モード';
        badge.style.background = 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))';
      } else {
        badge.textContent = `${provider.toUpperCase()} API 稼働中`;
        badge.style.background = 'linear-gradient(135deg, var(--accent-emerald), var(--accent-blue))';
      }
    }
  } catch (err) {
    console.error('Settings loading error:', err);
  }
}

// 3. Preset Templates Loader
function initPresets() {
  // Preset loader disabled for domain-agnostic generic mode.
}

// 4. Run Simulation
function initSimulation() {
  const form = document.getElementById('form-simulation');
  const btn = document.getElementById('btn-run-simulation');
  const spinner = document.getElementById('spinner-simulate');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const reqData = {
      systemName: document.getElementById('system-name').value,
      surveyInput: document.getElementById('survey-input').value
    };

    // Toggle loading UI
    btn.disabled = true;
    spinner.classList.remove('hidden');

    try {
      const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqData)
      });

      if (response.ok) {
        simulationData = await response.json();
        
        // Success animation and render
        showToast('シミュレーション完了！各タブで結果を確認できます。');
        
        // Go to Clones tab automatically to show results
        document.getElementById('nav-clones').click();
        
        // Render all panels
        renderUserClones(simulationData.user_clones);
        renderDuplicateClones(simulationData.duplicate_clones);
        renderDebateTimeline(simulationData.debate_logs);
        renderATDDArea(simulationData.atdd_gherkin, simulationData.playwright_code, simulationData.feasibility_feedback);
        renderQualityMetrics(simulationData.quality_metrics, simulationData.director_summary);
      } else {
        const errorData = await response.json();
        alert('シミュレーションに失敗しました: ' + (errorData.detail || '不明なエラー'));
      }
    } catch (err) {
      alert('通信中にエラーが発生しました: ' + err.message);
    } finally {
      btn.disabled = false;
      spinner.classList.add('hidden');
    }
  });
}

// Render: User Clones (利用者クローン)
function renderUserClones(users) {
  const container = document.getElementById('user-clones-container');
  container.innerHTML = '';

  if (!users || users.length === 0) {
    container.innerHTML = '<div class="no-data">利用者クローンデータがありません。</div>';
    return;
  }

  users.forEach(user => {
    const painPointsList = user.pain_points.map(p => `<li>${escapeHtml(p)}</li>`).join('');
    
    const card = document.createElement('div');
    card.className = 'persona-card fade-in';
    card.innerHTML = `
      <div class="persona-header">
        <div class="persona-avatar">${escapeHtml(user.name.substring(0, 1))}</div>
        <div class="persona-meta">
          <h3>${escapeHtml(user.name)}</h3>
          <span>役割: ${escapeHtml(user.role)} | 年齢: ${user.age}才</span>
        </div>
      </div>
      <div class="persona-body">
        <h4>🖥️ ITリテラシー</h4>
        <p>${escapeHtml(user.tech_savviness)}</p>
        
        <h4>⚠️ 課題（ペインポイント）</h4>
        <ul>${painPointsList}</ul>
        
        <h4>💡 期待するシステム要求</h4>
        <p>${escapeHtml(user.needs)}</p>
      </div>
    `;
    container.appendChild(card);
  });
}

// Render: Duplicate Clones (複製クローン)
function renderDuplicateClones(duplicates) {
  const tbody = document.getElementById('duplicate-clones-tbody');
  tbody.innerHTML = '';

  if (!duplicates || duplicates.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="center-text text-muted">複製クローンデータがありません。</td></tr>';
    return;
  }

  duplicates.forEach(clone => {
    const reliabilityClass = clone.reliability > 0.85 ? 'high' : 'medium';
    
    const tr = document.createElement('tr');
    tr.className = 'fade-in';
    tr.innerHTML = `
      <td><code>${escapeHtml(clone.id)}</code></td>
      <td><strong>${escapeHtml(clone.name)}</strong></td>
      <td><code>${escapeHtml(clone.base_id)}</code></td>
      <td>${escapeHtml(clone.role)}</td>
      <td class="center-text">${clone.age}</td>
      <td class="center-text">${escapeHtml(clone.tech_savviness)}</td>
      <td class="center-text"><strong>${Math.round(clone.reliability * 100)}%</strong></td>
      <td><span class="reliability-tag ${reliabilityClass}">${escapeHtml(clone.label)}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Render: Debate timeline with delay typing simulation (要求抽出ディベート)
function renderDebateTimeline(logs) {
  const container = document.getElementById('chat-container');
  container.innerHTML = '';

  if (!logs || logs.length === 0) {
    container.innerHTML = '<div class="no-data">議論ログデータがありません。</div>';
    return;
  }

  let delay = 300;
  
  logs.forEach((log, index) => {
    setTimeout(() => {
      const isPm = log.speaker.toLowerCase().includes('pm') || log.speaker.includes('プロジェクトマネージャー');
      const bubbleClass = isPm ? 'pm' : '';
      
      const msg = document.createElement('div');
      msg.className = `chat-message ${bubbleClass}`;
      msg.innerHTML = `
        <div class="chat-avatar">${escapeHtml(log.avatar)}</div>
        <div class="chat-bubble">
          <div class="chat-name">${escapeHtml(log.speaker)}</div>
          <div class="chat-text">${escapeHtml(log.text)}</div>
        </div>
      `;
      container.appendChild(msg);
      
      // Auto scroll to bottom
      container.scrollTop = container.scrollHeight;
    }, delay);
    
    delay += 1000; // Increment delay for sequential display
  });
}

// Render: Gherkin ATDD & Playwright scripts
function renderATDDArea(gherkin, playwright, feedback) {
  document.getElementById('code-gherkin').textContent = gherkin || 'Gherkinコードが生成されていません。';
  document.getElementById('code-playwright').textContent = playwright || 'Playwrightコードが生成されていません。';
  document.getElementById('feasibility-feedback').textContent = feedback || '評価フィードバックがありません。';
}

// Render: Quality metrics & Final validation report
function renderQualityMetrics(metrics, summary) {
  const container = document.getElementById('metrics-bars-container');
  container.innerHTML = '';

  if (!metrics) {
    container.innerHTML = '<div class="no-data">品質メトリクスデータがありません。</div>';
    return;
  }

  // Key mappings for ISO/IEC 25010 characteristic titles
  const keyMap = {
    functional_suitability: '機能適合性 (Functional Suitability)',
    performance_efficiency: '性能効率性 (Performance Efficiency)',
    compatibility: '互換性 (Compatibility)',
    usability: '使用性 (Usability)',
    reliability: '信頼性 (Reliability)',
    security: 'セキュリティ (Security)',
    maintainability: '保守性 (Maintainability)',
    portability: '移植性 (Portability)'
  };

  Object.entries(metrics).forEach(([key, val]) => {
    const row = document.createElement('div');
    row.className = 'metric-row';
    row.innerHTML = `
      <div class="metric-meta">
        <span class="metric-name">${keyMap[key] || key}</span>
        <span class="metric-val">${val}%</span>
      </div>
      <div class="metric-bar-bg">
        <div class="metric-bar-fill" style="width: 0%"></div>
      </div>
    `;
    container.appendChild(row);
    
    // Trigger animation frame to expand bar width smoothly
    setTimeout(() => {
      const fill = row.querySelector('.metric-bar-fill');
      if (fill) fill.style.width = `${val}%`;
    }, 100);
  });

  // Render Quality Manager notes based on metrics
  const notesContainer = document.getElementById('quality-manager-notes');
  let noteText = `【品質管理者による特性評価】\n\n`;
  if (metrics.usability >= 90) {
    noteText += `✅ **使用性 (Usability) が高評価 [${metrics.usability}%]**:\n一般ユーザーのペインポイント（画像認識の手間、画面構成の複雑さ）に対して、UI簡素化や自動化アシストが適切に要件化されています。\n\n`;
  } else {
    noteText += `⚠️ **使用性 (Usability) に改善の余地 [${metrics.usability}%]**:\n一般ユーザーの操作障壁を下げるためのUI・ナビゲーション設計が不足しています。操作ステップの削除が必要です。\n\n`;
  }
  
  if (metrics.reliability >= 85) {
    noteText += `✅ **信頼性 (Reliability) 合格基準 [${metrics.reliability}%]**:\n申請規程の自動整合チェックやサーバーバリデーションなど、入力エラー時の防御策が高レベルで設計されています。\n\n`;
  } else {
    noteText += `⚠️ **信頼性 (Reliability) 注意 [${metrics.reliability}%]**:\n注文重複決済や二重送信のリスクに対するガードレールが不十分です。非同期APIコール時の処理設計を見直してください。\n\n`;
  }

  noteText += `📌 **推奨されるテスト施策**:\n1. 統計複製クローンによる高負荷時および入力ゆらぎストレス評価テストの追加。\n2. 各外部API（決済・OCR・カルテ）障害時のモックフォールバック自動テストの実装。`;
  notesContainer.innerHTML = noteText;

  // Render Director report
  document.getElementById('director-report').textContent = summary || '最終報告書がまだありません。';
}

// 5. ATDD Periodic Spec Reviewer (定期レビューアー)
function initReviewer() {
  const btn = document.getElementById('btn-run-review');
  const spinner = document.getElementById('spinner-review');
  const specText = document.getElementById('spec-input');
  
  btn.addEventListener('click', async () => {
    const atddText = document.getElementById('code-gherkin').textContent;
    const docText = specText.value.trim();

    if (!docText) {
      alert('レビュー対象の設計書・仕様テキストを入力してください。');
      return;
    }
    if (atddText.includes('シミュレーションを実行すると')) {
      alert('先にダッシュボードで要求シミュレーションを実行し、ATDD基準を策定してください。');
      return;
    }

    btn.disabled = true;
    spinner.classList.remove('hidden');

    try {
      const response = await fetch('/api/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          specText: docText,
          atddGherkin: atddText
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Show status boxes
        const statusBox = document.getElementById('review-status-box');
        statusBox.classList.remove('hidden');
        
        document.getElementById('lbl-review-score').textContent = `${result.score}%`;
        document.getElementById('lbl-review-status').textContent = result.status;
        
        const detailsBox = document.getElementById('review-details');
        detailsBox.textContent = result.details;
        detailsBox.style.borderColor = result.score >= 90 ? 'var(--accent-emerald)' : 'var(--accent-rose)';
      } else {
        alert('仕様書レビューに失敗しました。');
      }
    } catch (err) {
      alert('エラーが発生しました: ' + err.message);
    } finally {
      btn.disabled = false;
      spinner.classList.add('hidden');
    }
  });
}

// 6. GitHub Integration (Commit Gherkin / Playwright to Repository)
function initGitHubCommit() {
  const modal = document.getElementById('github-modal');
  const btnGherkin = document.getElementById('btn-push-gherkin');
  const btnPlaywright = document.getElementById('btn-push-playwright');
  const btnCancel = document.getElementById('btn-modal-cancel');
  const btnSubmit = document.getElementById('btn-modal-submit');
  const spinnerModal = document.getElementById('spinner-modal');
  
  const pathInput = document.getElementById('commit-path');
  const messageInput = document.getElementById('commit-message');
  
  let activeContent = '';
  
  // Gherkin commit trigger
  btnGherkin.addEventListener('click', () => {
    if (!simulationData) {
      alert('シミュレーションが完了していません。');
      return;
    }
    if (!currentSettings.githubToken || !currentSettings.githubRepo) {
      alert('先に「システム設定」タブでGitHubのアクセストークンとリポジトリ名を設定してください。');
      document.getElementById('nav-settings').click();
      return;
    }
    
    // Setup modal inputs
    const baseName = simulationData.domain === 'expense' ? 'expense' : (simulationData.domain === 'medical' ? 'medical' : 'checkout');
    pathInput.value = `tests/atdd_${baseName}.feature`;
    messageInput.value = `docs: add Gherkin acceptance criteria for ${baseName}`;
    activeContent = document.getElementById('code-gherkin').textContent;
    
    // Open Modal
    modal.classList.remove('hidden');
  });

  // Playwright commit trigger
  btnPlaywright.addEventListener('click', () => {
    if (!simulationData) {
      alert('シミュレーションが完了していません。');
      return;
    }
    if (!currentSettings.githubToken || !currentSettings.githubRepo) {
      alert('先に「システム設定」タブでGitHubのアクセストークンとリポジトリ名を設定してください。');
      document.getElementById('nav-settings').click();
      return;
    }
    
    // Setup modal inputs
    const baseName = simulationData.domain === 'expense' ? 'expense' : (simulationData.domain === 'medical' ? 'medical' : 'checkout');
    pathInput.value = `tests/atdd_${baseName}.spec.js`;
    messageInput.value = `test: add automated Playwright test for ${baseName}`;
    activeContent = document.getElementById('code-playwright').textContent;
    
    // Open Modal
    modal.classList.remove('hidden');
  });

  // Close modal
  btnCancel.addEventListener('click', () => {
    modal.classList.add('hidden');
  });

  // Push Commit execution
  btnSubmit.addEventListener('click', async () => {
    const path = pathInput.value.trim();
    const commitMsg = messageInput.value.trim();

    if (!path || !commitMsg) {
      alert('すべての項目を入力してください。');
      return;
    }

    btnSubmit.disabled = true;
    spinnerModal.classList.remove('hidden');

    try {
      const response = await fetch('/api/github/push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: path,
          content: activeContent,
          commitMessage: commitMsg
        })
      });

      const res = await response.json();
      if (response.ok) {
        modal.classList.add('hidden');
        showToast('Commit Succeeded! Link: <a href="' + res.url + '" target="_blank" style="color: #050510; font-weight: bold; text-decoration: underline;">GitHubで表示</a>');
      } else {
        alert('コミット失敗: ' + (res.detail || '不明なエラー'));
      }
    } catch (err) {
      alert('エラーが発生しました: ' + err.message);
    } finally {
      btnSubmit.disabled = false;
      spinnerModal.classList.add('hidden');
    }
  });
}

// Helper: Show custom toast notification
function showToast(htmlMessage) {
  const toast = document.getElementById('toast');
  toast.innerHTML = htmlMessage;
  toast.classList.remove('hidden');
  
  // Auto-hide toast after 4.5 seconds
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 4500);
}

// Helper: Escape HTML characters for rendering
function escapeHtml(text) {
  if (typeof text !== 'string') return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
