import json
import httpx
import re
import random
from typing import Dict, Any, List

class AgentEngine:
    def __init__(self):
        pass

    def run_simulation(self, survey_input: str, system_name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the simulation. If API keys are provided in settings, calls LLMs.
        Otherwise, falls back to context-aware mock simulation.
        """
        use_mock = True
        api_key = settings.get("apiKey", "")
        provider = settings.get("provider", "mock")
        model_name = settings.get("model", "gemini-2.5-flash")

        if api_key and provider != "mock":
            use_mock = False

        if use_mock:
            return self._run_mock_simulation(survey_input, system_name)
        else:
            return self._run_llm_simulation(survey_input, system_name, provider, api_key, model_name)

    def _run_mock_simulation(self, survey_input: str, system_name: str) -> Dict[str, Any]:
        # Keyword-based matching to tailor the mock output to the user's system name/survey
        keywords = survey_input.lower() + " " + system_name.lower()
        
        # Determine domain
        if "経費" in keywords or "expense" in keywords or "申請" in keywords:
            domain = "expense"
        elif "ホテル" in keywords or "hotel" in keywords:
            domain = "hotel"
        elif "病院" in keywords or "クリニック" in keywords or "予約" in keywords or "medical" in keywords or "doctor" in keywords:
            domain = "medical"
        else:
            domain = "ecommerce"  # default

        # 1. Utilizer Clones (利用者クローン)
        user_clones = []
        if domain == "expense":
            user_clones = [
                {
                    "id": "user_1",
                    "name": "佐藤 美咲 (佐藤さん)",
                    "role": "一般社員 (申請者)",
                    "age": 28,
                    "tech_savviness": "中",
                    "pain_points": [
                        "スマホから領収書をアップロードする時の画像認識の精度が低く、手動修正が多い。",
                        "勘定科目の選択肢が多すぎて、どれを選べばいいか分からない。"
                    ],
                    "needs": "数タップで申請が完了するシンプルな画面と、AIによる自動仕訳機能。"
                },
                {
                    "id": "user_2",
                    "name": "田中 健一 (田中課長)",
                    "role": "管理職 (承認者)",
                    "age": 45,
                    "tech_savviness": "低",
                    "pain_points": [
                        "外出先で承認申請がたまっているが、モバイルUIが使いにくくてPCを開くまで放置してしまう。",
                        "不適切な申請（二重申請や上限超過）をシステム側で事前に弾いてほしい。"
                    ],
                    "needs": "プッシュ通知からの1クリック承認と、ポリシー違反の自動警告アラート。"
                }
            ]
        elif domain == "hotel":
            user_clones = [
                {
                    "id": "user_1",
                    "name": "上田 和樹 (上田さん)",
                    "role": "出張頻度が高いビジネスパーソン (一般購入者)",
                    "age": 51,
                    "tech_savviness": "高",
                    "pain_points": [
                        "宿泊する日付が決まっているのに、その日付で予約可能（空室あり）なプランだけを一覧表示してくれない。",
                        "空き状況を確認するためだけに、プラン詳細ページを一つずつ開いて確かめるのが非常に手間で面倒。"
                    ],
                    "needs": "宿泊日を指定した際、実際に空室があり予約可能なプランだけを即座にダイレクトに一覧表示・確認できる仕組み。"
                },
                {
                    "id": "user_2",
                    "name": "佐藤 恵美 (佐藤さん)",
                    "role": "ホテル側の販売プラン管理・運用担当者",
                    "age": 42,
                    "tech_savviness": "中",
                    "pain_points": [
                        "急な団体予約が入った際、一般客向けの特定日プランを一件ずつ手動で売止（クローズ）する作業が煩雑でミスが起きやすい。",
                        "支払い内訳（消費税やサービス料）のカスタマイズ表示設計が硬直的である。"
                    ],
                    "needs": "管理画面での複数プラン一括売止（クローズ）機能と、支払い料金の内訳明示のカスタム設計。"
                }
            ]
        elif domain == "medical":
            user_clones = [
                {
                    "id": "user_1",
                    "name": "鈴木 茂 (鈴木さん)",
                    "role": "高齢の患者",
                    "age": 68,
                    "tech_savviness": "低",
                    "pain_points": [
                        "文字サイズが小さくて読めず、予約完了までのステップ数が多すぎる。",
                        "予約日の前日に忘れないよう電話やSMSでリマインダーが欲しい。"
                    ],
                    "needs": "大きな文字とボタンによるシンプルな3ステップ予約画面。"
                },
                {
                    "id": "user_2",
                    "name": "小林 玲子 (小林先生)",
                    "role": "クリニックの院長・医師",
                    "age": 52,
                    "tech_savviness": "中",
                    "pain_points": [
                        "予約枠の間隔調整や、急な休診時の自動キャンセル通知機能がない。",
                        "電子カルテ連携が手動のため、二重登録の手間が発生している。"
                    ],
                    "needs": "柔軟なスケジュール枠管理と、電子カルテAPI連携。"
                }
            ]
        else:  # E-commerce
            user_clones = [
                {
                    "id": "user_1",
                    "name": "高橋 優斗 (高橋さん)",
                    "role": "頻繁に利用する一般購入者",
                    "age": 24,
                    "tech_savviness": "高",
                    "pain_points": [
                        "決済画面の読み込みが遅く、エラーが出て二重決済になっていないか不安になる。",
                        "クレジットカード情報を毎回入力するのが面倒。"
                    ],
                    "needs": "Google PayやApple Payなどのワンクリック決済の導入と、超高速なローディング。"
                },
                {
                    "id": "user_2",
                    "name": "渡辺 明美 (渡辺さん)",
                    "role": "EC運用の管理担当者",
                    "age": 39,
                    "tech_savviness": "中",
                    "pain_points": [
                        "クーポンの割引適用ロジックが複雑で、購入手続きでエラーになった顧客からの問い合わせが多い。",
                        "注文変更やキャンセル処理の管理画面が使いにくい。"
                    ],
                    "needs": "クーポン適用エラー発生時の詳細ログ機能と、直感的なステータス変更UI。"
                }
            ]

        # 2. Duplicate Clones (複製クローン)
        duplicate_clones = []
        names_pool = ["渡辺", "山本", "中村", "小林", "加藤", "吉田", "山田", "佐々木", "山口", "斉藤"]
        
        # Scale User 1
        for i in range(1, 4):
            tech = random.choice(["低", "中", "高"])
            consistency = round(random.uniform(0.78, 0.95), 2)
            bias = round(random.uniform(0.01, 0.10), 2)
            reliability = round(consistency * (1 - bias), 2)
            
            duplicate_clones.append({
                "id": f"dup_{i}",
                "base_id": "user_1",
                "name": f"{random.choice(names_pool)} {random.choice(['一郎', '洋子', '健二', '美香', '哲也'])}",
                "role": user_clones[0]["role"],
                "age": user_clones[0]["age"] + random.randint(-5, 5),
                "tech_savviness": tech,
                "reliability": reliability,
                "label": "信頼性: 高" if reliability > 0.85 else "信頼性: 中",
                "simulated_behavior": f"基本行動パターンは {user_clones[0]['name']} と類似。デバイス環境や通信速度を変動させてテスト。"
            })
            
        # Scale User 2
        for i in range(4, 7):
            tech = random.choice(["低", "中", "高"])
            consistency = round(random.uniform(0.70, 0.90), 2)
            bias = round(random.uniform(0.05, 0.15), 2)
            reliability = round(consistency * (1 - bias), 2)
            
            duplicate_clones.append({
                "id": f"dup_{i}",
                "base_id": "user_2",
                "name": f"{random.choice(names_pool)} {random.choice(['昭雄', '和代', '正治', '直美', '博'])}",
                "role": user_clones[1]["role"],
                "age": user_clones[1]["age"] + random.randint(-5, 5),
                "tech_savviness": tech,
                "reliability": reliability,
                "label": "信頼性: 高" if reliability > 0.85 else "信頼性: 中",
                "simulated_behavior": f"基本行動パターンは {user_clones[1]['name']} と類似。特定の承認パターン・イレギュラーケースを中心に検証。"
            })

        # 3. QA Specialist Clones & 4. PM Clone Debate (討論ログ)
        debate_logs = []
        if domain == "expense":
            debate_logs = [
                {
                    "speaker": "QA1 (テスト設計担当)",
                    "avatar": "🤖",
                    "text": "利用者クローンの佐藤さん（一般社員）の最大の課題は『領収書画像認識のやり直し』と『勘定科目迷子』ですね。まずは領収書アップロード機能に絞って要求を整理しましょう。"
                },
                {
                    "speaker": "QA2 (UX品質担当)",
                    "avatar": "🔍",
                    "text": "そうですね。それに加えて、田中課長（承認者）の『外出先からの1クリック承認』も極めて重要です。PCを開くこと自体が承認遅延のボトルネックになっています。モバイルファーストの承認要求を盛り込みましょう。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "一般社員の申請負荷削減には大いに賛成です。ただ、勘定科目の自動推測については、会社の経費規程との整合性チェックが必要です。誤判定したまま申請されると経理の二重チェックが発生するため、『推測根拠を表示し、確認させるチェックボックス』を必須要件にしたいです。"
                },
                {
                    "speaker": "QA1 (テスト設計担当)",
                    "avatar": "🤖",
                    "text": "なるほど、了解です。では、『AIが領収書から読み取った日付・金額・品名から、もっとも可能性の高い勘定科目をTop3で提示し、そのうちの1つをチェック選択して申請する』という二段階の確認フローとしてユーザーストーリーを作成します。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "素晴らしい！それであれば経理チームの懸念も解消されます。そのフローで進めてください。"
                }
            ]
        elif domain == "hotel":
            debate_logs = [
                {
                    "speaker": "QA1 (テスト設計担当)",
                    "avatar": "🤖",
                    "text": "一般利用者の上田さんはITリテラシーが高く、無駄なステップを激しく嫌います。宿泊日を入力しているなら『空室のあるプランのみ』を表示し、満室プランは最初から除外するか非活性化する要求が必要です。"
                },
                {
                    "speaker": "QA2 (UX品質担当)",
                    "avatar": "🔍",
                    "text": "賛成です。いちいち詳細画面を開かないと空室状況がわからないUIは、ユーザーをイライラさせます。また、上田さんの回答によると『金額の内訳がはっきり表示されること』が重要な狩野モデルA（魅力品質）に入っています。カート内訳と計算の正確さの担保も要件に加えましょう。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "空室プランのみの絞り込み表示と、価格内訳の明示はぜひ要件に組み込みましょう。ただ、在庫システム（PMS）との連動ラグにより、検索結果画面で『空室』でも、詳細へ遷移する間に『満室』になる可能性があります。これによるブッキング防止策はどうしますか？"
                },
                {
                    "speaker": "QA1 (テスト設計担当)",
                    "avatar": "🤖",
                    "text": "では『プラン選択時』と『予約確定ボタン押下時』の二箇所で、サーバーサイドでPMSへ空室のリアルタイム照会APIを呼び出し、在庫切れの場合は速やかに「ご指定のプランは満室となりました」と表示して処理を安全にアボートする設計にします。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "素晴らしいです。二段階のバリデーションがあれば在庫ズレによるトラブルを防止できます。さらに運用者の佐藤さんから要望されている『プラン一括売止』の処理も満室時には自動適用されるルールを盛り込みましょう。その仕様でユーザーストーリーをまとめます。"
                }
            ]
        elif domain == "medical":
            debate_logs = [
                {
                    "speaker": "QA1 (テスト設計担当)",
                    "avatar": "🤖",
                    "text": "鈴木さん（高齢患者）はスマートフォンでの複雑な操作がボトルネックになっています。カレンダー選択や会員ログインなどの操作が難しいため、パスワードレスな認証と超シンプルな予約確認プロセスが必要不可欠です。"
                },
                {
                    "speaker": "QA2 (UX品質担当)",
                    "avatar": "🔍",
                    "text": "はい、特に電話番号と生年月日だけの入力で認証が通る仕組みや、予約内容が視覚的に大きく表示されるUIを要求に含めるべきです。また院長の小林先生の『電子カルテ連携』ですが、これは基幹システムとなるため、予約成立時のリアルタイムデータシンクが必要ですね。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "高齢の患者さん向けに操作ステップを極限まで減らすという方向性は合意します。ただ、セキュリティの観点から『電話番号＋生年月日』だけだと誤入力により他人の情報が見えてしまうリスクがあります。SMSでの1回限りの4桁ワンタイムパスワード認証を挟むべきです。これなら鈴木さんも数字4桁を打ち込むだけなので大きな障壁にはならないと考えます。"
                },
                {
                    "speaker": "QA2 (UX品質担当)",
                    "avatar": "🔍",
                    "text": "納得しました。セキュリティと使いやすさを両立させるため、SMSでのワンタイムパスワードを用いた認証ステップをストーリーに加えます。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "電子カルテ連携については、通信障害時のオフライン再同期バッチ処理も追加要求としましょう。リアルタイム接続が切れたときに予約情報が消失しないようにするためです。"
                }
            ]
        else:  # E-commerce
            debate_logs = [
                {
                    "speaker": "QA1 (テスト設計担当)",
                    "avatar": "🤖",
                    "text": "高橋さん（若年層・一般購入者）はスピード重視です。決済画面の読み込み待ちや、クレジットカード情報の都度入力に対する不満が非常に高い。一方、管理担当の渡辺さんはクーポン適用トラブルでの問い合わせ対応コストを削減したいと考えています。"
                },
                {
                    "speaker": "QA2 (UX品質担当)",
                    "avatar": "🔍",
                    "text": "購入完了までの遷移回数を減らすため、カート画面から直接Apple PayやGoogle Payを選択して即時決済する『エクスプレスチェックアウト』を要件に入れましょう。これなら離脱率も大幅に下がります。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "決済スピードアップは売上直結なので最優先ですね。ただ、クーポンが二重適用されたり、特定条件（例: 合計金額未満）で不正適用されるバグは防がなければなりません。エクスプレス決済時も裏側でカートのバリデーションAPIが完全にチェックを行う必要があります。"
                },
                {
                    "speaker": "QA1 (テスト設計担当)",
                    "avatar": "🤖",
                    "text": "確かに。では、『購入ボタンが押された後、決済ゲートウェイにトークンを送る前に、最新のカートステータス、商品在庫、クーポン適用可否をサーバーサイドでバリデーションし、問題があればエラーメッセージを出して決済処理を安全にアボートする』というストーリーにします。"
                },
                {
                    "speaker": "PM (プロジェクトマネージャー)",
                    "avatar": "💼",
                    "text": "はい、その安全機構は必須です。これなら在庫切れによる決済エラーなどの問題も事前に防止できます。このストーリーで合意しましょう。"
                }
            ]

        # 5. Automation Engineer (自動化エンジニア) ATDD & Gherkin / Playwright
        atdd_gherkin = ""
        playwright_code = ""
        feasibility_feedback = ""

        if domain == "expense":
            atdd_gherkin = """Feature: 経費精算の領収書アップロードと自動仕訳
  一般社員が経費精算の手間を最小限に抑えるため、
  領収書画像から情報を自動抽出し、正しい勘定科目を提示して申請できるようにする。

  Scenario: 領収書のアップロードと自動仕訳の確認・申請
    Given ユーザーは経費申請作成画面に遷移している
    When 「領収書アップロード」ボタンを押し、"receipt_2026.png" を選択する
    Then 領収書のOCR解析が走り、日付「2026/06/20」、金額「15,000円」、取引先「六本木レストラン」が自動入力される
    And 勘定科目の推奨選択肢として「会議費(確率:85%)」「交際費(確率:12%)」「旅費交通費(確率:3%)」が表示される
    When 「会議費」を選択し、「利用規程に準拠していることを確認しました」のチェックボックスをオンにする
    And 「申請する」ボタンを押す
    Then 経費申請が完了し、申請IDが表示され、申請ステータスが「承認待ち」となる"""

            playwright_code = """import { test, expect } from '@playwright/test';

test.describe('経費精算自動化テスト', () => {
  test('領収書アップロードから申請完了までのフロー', async ({ page }) => {
    // 1. 経費申請作成画面にアクセス
    await page.goto('/expense/new');
    
    // 2. 領収書のアップロード (input[type=file] のロケーター)
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.locator('#receipt-upload-btn').click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles('test-data/receipt_2026.png');
    
    // 3. OCRローディングと自動入力の検証
    // スピナーの非表示を待つ
    await page.locator('.ocr-spinner').waitFor({ state: 'detached', timeout: 10000 });
    
    // 自動入力されたデータのチェック
    await expect(page.locator('#receipt-date')).toHaveValue('2026/06/20');
    await expect(page.locator('#receipt-amount')).toHaveValue('15000');
    await expect(page.locator('#receipt-vendor')).toHaveValue('六本木レストラン');
    
    // 4. 勘定科目推奨の検証と選択
    const categorySelect = page.locator('#expense-category-selector');
    await expect(categorySelect.locator('.recommendation-badge').first()).toContainText('会議費');
    await categorySelect.locator('.recommendation-item').first().click();
    
    // 5. 規程チェックボックスと申請処理
    await page.locator('#compliance-agreement-checkbox').check();
    await page.locator('#submit-application-btn').click();
    
    // 6. 完了確認
    await expect(page.locator('.success-toast')).toBeVisible();
    await expect(page.locator('#application-status')).toContainText('承認待ち');
  });
});"""
            feasibility_feedback = """【自動化実現性の評価結果】
- ロケーター: 主要入力エリアはIDが振られており特定は容易。ただし「推奨バッジ」や「推奨選択肢」の動的ポップアップは、DOM描画タイミングに合わせて `waitFor` を挟む必要がある。
- 手順 of 明確化: アップロード完了 -> OCR処理 -> 推奨表示のプロセスが非同期になるため、暗黙のウェイトではなくスピナーの状態遷移をアサーション対象にする設計が必要。
- 前提条件とデータ: テスト用の領収書画像「receipt_2026.png」がリポジトリ内に配備されていること。またOCRサービスのモックサーバー環境（外部APIへの依存排除）がローカルテスト実行時に必要。
- 総合評価: 実装可能 (Feasible)。OCRのモック化さえ確立すれば、Playwrightで100%安定稼働する。"""

        elif domain == "hotel":
            atdd_gherkin = """Feature: 宿泊日指定による空室プランのみの絞り込み表示と予約
  ホテルの利用者が無駄な操作をせずにスムーズに予約完了できるよう、
  指定した宿泊日に実際に予約可能なプランだけを一覧表示し、空室バリデーションを経て予約できること。

  Scenario: 指定日の空室プランのみが表示され、ワンクリックで予約へ進む
    Given ユーザーはホテル予約サイトのトップページで宿泊日に「2026/07/10」を指定している
    When 「空室のあるプランを検索」ボタンを押す
    Then 指定日に実際に空室があるプラン「ビジネス出張応援プラン」のみが一覧に表示される
    And 満室のプランや、その日に提供されていないプランは表示されない
    When プランの「このプランを選択する」を押す
    Then システム内部でリアルタイム空室照会APIが走り、空室あり（在庫数 > 0）が再確認される
    And 支払い金額の内訳として「基本宿泊料 10,000円」「消費税 1,000円」が明記された確認画面に遷移する"""

            playwright_code = """import { test, expect } from '@playwright/test';

test.describe('ホテル予約サイト 空室検索・予約フローテスト', () => {
  test('指定日の空室のみが表示され、選択時にリアルタイム在庫バリデーションが走る', async ({ page }) => {
    // 1. トップページ遷移と日付指定
    await page.goto('/hotel/search');
    await page.locator('#checkin-date').fill('2026-07-10');
    await page.locator('#search-vacant-btn').click();
    
    // 2. 空室プランのみ表示されていることを確認
    const planList = page.locator('.hotel-plan-list');
    await expect(planList.locator('.plan-item')).toHaveCount(1);
    await expect(planList.locator('.plan-title').first()).toContainText('ビジネス出張応援プラン');
    
    // 3. プラン選択と在庫APIバリデーション検証
    await page.locator('.btn-select-plan').first().click();
    
    // 4. 内訳金額がはっきり表示されていることの検証 (Kano A)
    const breakdown = page.locator('.price-breakdown');
    await expect(breakdown).toBeVisible();
    await expect(breakdown.locator('.base-price')).toContainText('¥10,000');
    await expect(breakdown.locator('.tax-amount')).toContainText('¥1,000');
    
    // 5. 確定画面遷移確認
    await expect(page.locator('#booking-confirm-title')).toBeVisible();
  });
});"""
            feasibility_feedback = """【自動化実現性の評価結果】
- ロケーター: 日付入力フィールド（#checkin-date）や検索ボタンは標準的なID指定で動作可能。ホテルプラン一覧の描画はPMS連携のAPI応答時間に左右されるため、リストが表示されるまで `.plan-item` の `waitFor` 処理を組み込むのが必須。
- 手順の明確化: 選択時のリアルタイム照会APIの遅延を考慮し、ローディングスピナーが消えたことを検知してから価格内訳のアサーションを行う設計とします。
- 前提条件とデータ: 2026年7月10日に該当ホテルの部屋在庫が登録されているテストデータ（PMSモック）の事前投入が必要です。
- 総合評価: 実装可能 (Feasible)。日付ごとの在庫データ初期化と登録プロセスさえ確立すれば、Playwrightで極めて安定した予約自動テストが書けます。"""

        elif domain == "medical":
            atdd_gherkin = """Feature: 患者向け簡単予約システム
  高齢の患者でも迷わずに、SMSによる簡易認証を経て
  カレンダーから最短3ステップで予約を完了できるようにする。

  Scenario: 認証から予約完了までの3ステップ操作
    Given ユーザーは予約サイトのトップページにアクセスしている
    When 「簡単予約をはじめる」ボタンを押す
    And 携帯電話番号「09012345678」と生年月日「1958/05/10」を入力して「認証コード送信」を押す
    Then 入力した携帯電話宛てにSMSで4桁の認証コードが届く
    When 認証コード入力欄に「4321」を入力して「次へ」を押す
    And 表示された予約空き枠カレンダーから「6月25日 10:00」を選択する
    And 「この内容で予約を確定する」を押す
    Then 画面に「予約が確定しました」と大きな文字で表示され、確認用SMSが送信される"""

            playwright_code = """import { test, expect } from '@playwright/test';

test.describe('簡単予約フロー自動化テスト', () => {
  test('高齢患者の簡単予約完了フロー', async ({ page }) => {
    // 1. トップページ遷移
    await page.goto('/booking');
    await page.locator('#start-booking-btn').click();
    
    // 2. 携帯電話番号・生年月日入力
    await page.locator('#phone-number').fill('09012345678');
    await page.locator('#birth-date').fill('1958-05-10');
    await page.locator('#send-code-btn').click();
    
    // 3. SMS認証コードの入力 (テスト環境では固定コード '4321' が通るようにモック化)
    await page.locator('#otp-input').fill('4321');
    await page.locator('#verify-code-btn').click();
    
    // 4. カレンダーから日時選択
    // 2026年6月25日 10:00 のセルをクリック
    const slot = page.locator('[data-date="2026-06-25"][data-time="10:00"]');
    await slot.scrollIntoViewIfNeeded();
    await slot.click();
    
    // 5. 予約確定
    await page.locator('#confirm-booking-btn').click();
    
    // 6. 完了表示確認 (アクセシビリティ考慮の巨大テキスト)
    const successHeader = page.locator('#booking-success-title');
    await expect(successHeader).toBeVisible();
    await expect(successHeader).toHaveCSS('font-size', /32px|40px/); // 大きな文字の確認
  });
});"""
            feasibility_feedback = """【自動化実現性の評価結果】
- ロケーター: カレンダーのセル部分は `data-date` および `data-time` 属性がカスタムで定義されている前提が必要。無ければ曜日や日付ベースでのテキスト検索になるため、安定性が落ちる。
- 手順の明確化: SMS認証コードの送信と受信という外部連携プロセスがあるため、テスト実行環境では認証コード生成ロジックをバイパス（または常に特定のテスト用番号に対して '4321' を通す）する設定が必要。
- 前提条件とデータ: カレンダーの空き枠情報がデータベース上で存在している状態を作るための、API/シードデータ整備が必要（常に明日以降の空き枠を挿入する仕組み）。
- 総合評価: 実装可能 (Feasible)。SMSのモック処理と、日付シードデータの定期挿入があれば、容易に自動化可能。"""

        else:  # E-commerce
            atdd_gherkin = """Feature: カート決済の高速化と安全な注文バリデーション
  購入者の離脱を防ぐためのワンクリック高速決済を導入しつつ、
  裏側でクーポンの整合性と在庫チェックを厳格に行い、誤った決済を防ぐ。

  Scenario: エクスプレスチェックアウトを利用した高速注文決済
    Given ユーザーはショッピングカートに商品「スマートウォッチ」を入れている
    And カート内で「SUMMER26」クーポンを適用している
    When 「Google Payで支払う」ボタンを押す
    Then 内部APIで在庫「スマートウォッチ」が残り1個以上あること、およびクーポン割引「1,000円」が有効であることを裏で検証する
    When 決済ゲートウェイから成功のコールバックを受信する
    Then 注文手続きが即座に完了し、注文完了画面に遷移し、在庫数が1減少する"""

            playwright_code = """import { test, expect } from '@playwright/test';

test.describe('ECサイト決済自動化テスト', () => {
  test('Google Payエクスプレスチェックアウトの完了フロー', async ({ page }) => {
    // 1. カート画面に遷移
    await page.goto('/cart');
    
    // 商品が存在することの確認
    await expect(page.locator('.cart-item-name')).toContainText('スマートウォッチ');
    
    // クーポンコードの適用
    await page.locator('#coupon-input').fill('SUMMER26');
    await page.locator('#apply-coupon-btn').click();
    await expect(page.locator('#discount-amount')).toContainText('-¥1,000');
    
    // 2. Google Payボタンのクリック
    // iframe内のボタン、またはカスタムボタンロケーターの指定
    const googlePayBtn = page.locator('#google-pay-button-container iframe').contentFrame().locator('.gpay-button');
    // もしくはテスト環境用モック決済ボタン
    // const googlePayBtn = page.locator('#mock-gpay-btn');
    await googlePayBtn.click();
    
    // 3. 決済ポップアップ/処理の完了確認
    // 注文成功メッセージ
    await expect(page.locator('.order-complete-message')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('.order-id-label')).not.toBeEmpty();
  });
});"""
            feasibility_feedback = """【自動化実現性の評価結果】
- ロケーター: Google Pay や Apple Pay の決済ボタンは通常サードパーティのセキュアな iframe 内部に配置されており、Playwrightから直接操作するにはセキュリティ制限がかかる可能性が極めて高い。
- 代替アプローチ: テスト環境では、決済プロバイダのSDKを「テスト用モックゲートウェイ」に差し替えるスイッチをフロントエンドに実装し、iframeを介さずにシミュレートするテスト専用ボタン (`#mock-gpay-btn`) を表示・操作させる手法が必須。
- 前提条件とデータ: 対象商品「スマートウォッチ」の在庫数があらかじめ1個以上登録されており、且つ「SUMMER26」クーポンコードがデータベース側で利用可能に設定されている必要がある。
- 総合評価: 要調整 (Needs Work)。生のGoogle Payボタンを直接叩くテストは難しいため、テスト環境でのモック決済APIの導入が自動テストの成否を分ける。"""

        # 6. ATDD Periodic Reviewer (定期レビューアー)
        review_result = {
            "score": 94 if domain == "hotel" else (92 if domain == "expense" or domain == "medical" else 85),
            "status": "ATDD準拠 (合格)" if domain != "ecommerce" else "改善要求あり (再確認)",
            "details": ""
        }

        if domain == "expense":
            review_result["details"] = """【要件定義書・基本設計書レビュー結果】
- 適合度: 92%
- 準拠状況: 作成された設計書『経費精算システム基本設計 ver1.2』とATDDを突き合わせました。
  - 設計書側の「3.2 領収書アップロード処理」において、OCR後の「勘定科目推奨の表示（Top3）」および「その理由」について言及されていることを確認しました。
  - また「3.5 申請処理」においても、利用規約/規程準拠のチェックボックスが必須バリデーションになっている設計が仕様化されており、ATDD基準を満たしています。
- 改善推奨項目: 
  - OCR処理が長時間（5秒以上）かかった際のタイムアウト設計、およびオフライン状態でのエラーハンドリング設計が設計書内に記述されていません。ユーザーの離脱を招く可能性があるため、「30秒でタイムアウトし手動入力に切り替える旨のダイアログを表示する」等の文言を追加してください。"""
        elif domain == "hotel":
            review_result["details"] = """【要件定義書・基本設計書レビュー結果】
- 適合度: 94%
- 準拠状況: 『ホテル予約機能要件定義書v1.1』とATDD基準を照合しました。
  - 要件定義の「4.1 検索機能」において、宿泊日指定時に在庫管理DBの空室テーブルとアウタージョインし、残室数1以上のプランのみをビューに出力するロジックが定義されています。
  - 「4.3 料金表示」についても、税・サービス料・割引適用額のそれぞれを個別の項目として内訳明記する画面レイアウトが設計されており、ユーザー上田様のペインポイントに対する解決要件（KanoモデルA）を満たしています。
- 改善推奨項目:
  - 予約詳細画面から「前回の予約履歴を参照したワンクリック再予約機能」についての仕様記述が漏れています（KanoモデルC）。リピート利用者の利便性向上のため、マイページからの『前と同じ内容で再予約』ボタンの仕様を追加してください。"""
        elif domain == "medical":
            review_result["details"] = """【要件定義書・基本設計書レビュー結果】
- 適合度: 95%
- 準拠状況: 作成された仕様書『患者予約フロー設計書v2.0』とATDDを照合。
  - 「2.1 SMS認証処理」において、入力ミスを防ぐための生年月日チェックと、4桁のワンタイムキーを3分間有効とする仕様が明記されています。
  - 画面UI定義においても、「文字サイズはブラウザ標準の1.5倍（24px以上）をデフォルトとする」というアクセシビリティ仕様が書かれており、高齢者ユーザー向けのATDD要件と完全に一致しています。
- 改善推奨項目:
  - 電子カルテ連携部分において、通信切断時のリトライ間隔と回数が未定義です。カルテ連携のキュー詰まりを防ぐためのリトライ限界数（例: 最大3回）を仕様書に追記してください。"""
        else: # ecommerce
            review_result["details"] = """【要件定義書・基本設計書レビュー結果】
- 適合度: 85%
- 準拠状況: 作成された仕様書『チェックアウト画面・決済仕様書v1.0』とATDDを照合。
  - クーポン割引適用のサーバーサイドバリデーションは「第4章 在庫・クーポン検証ロジック」に詳細に記述されており、ATDDで求めた決済前バリデーションに合致しています。
- 違反項目 (改善要求):
  - エクスプレスチェックアウト（Google Pay等）での決済エラー時、「カート画面に戻りエラー原因（クーポン無効など）を赤字で表示する」というエラー文言表示プロセスが仕様書上に記載されていません。決済が単に『失敗した』と表示されるだけでは、利用時品質（Usability）の低下につながります。エラー発生時のリカバリーフローを追記してください。"""

        # 7. General Director (総合指揮者)
        director_summary = f"""【総合指揮者レポート】
本システム「{system_name}」に対する実ユーザー（クローン）の要求抽出から、自動化テストコード(ATDD)設計、仕様書レビューまでの一連 of クローン協調プロセスが完了しました。

我々の最終ゴールは『実ユーザーが本当に必要とする、妥当性のあるシステム』の構築です。
今回のシミュレーション結果、一般ユーザー・管理側ユーザーの双方の痛み（ペインポイント）を捉えたユーザーストーリーを策定し、それを満たす自動化ATDDを定義しました。
この基準に沿って定期レビューを行うことで、本物のユーザーが直面するはずだった「使いにくさによる離脱」「運用コストの肥大化」といった潜在リスクを、開発開始前に高精度で検知できています。
引き続き、本ATDD基準をCI環境に組み込み、開発進捗と妥当性の乖離を監視し続けてください。"""

        # 8. Quality Manager (品質管理者) ISO/IEC 25010 metrics
        # ISO/IEC 25010 characteristics
        if domain == "expense":
            quality_metrics = {
                "functional_suitability": 90,
                "performance_efficiency": 78,
                "compatibility": 85,
                "usability": 95,
                "reliability": 88,
                "security": 92,
                "maintainability": 80,
                "portability": 75
            }
        elif domain == "hotel":
            quality_metrics = {
                "functional_suitability": 94,
                "performance_efficiency": 88,
                "compatibility": 92,
                "usability": 96,
                "reliability": 90,
                "security": 90,
                "maintainability": 84,
                "portability": 80
            }
        elif domain == "medical":
            quality_metrics = {
                "functional_suitability": 95,
                "performance_efficiency": 82,
                "compatibility": 70,
                "usability": 98,
                "reliability": 90,
                "security": 96,
                "maintainability": 85,
                "portability": 80
            }
        else: # ecommerce
            quality_metrics = {
                "functional_suitability": 88,
                "performance_efficiency": 95,
                "compatibility": 90,
                "usability": 85,
                "reliability": 82,
                "security": 94,
                "maintainability": 78,
                "portability": 85
            }

        return {
            "domain": domain,
            "user_clones": user_clones,
            "duplicate_clones": duplicate_clones,
            "debate_logs": debate_logs,
            "atdd_gherkin": atdd_gherkin,
            "playwright_code": playwright_code,
            "feasibility_feedback": feasibility_feedback,
            "review_result": review_result,
            "director_summary": director_summary,
            "quality_metrics": quality_metrics
        }

    def _run_llm_simulation(self, survey_input: str, system_name: str, provider: str, api_key: str, model_name: str) -> Dict[str, Any]:
        """
        Runs the actual LLM-based simulation.
        Queries LLM multiple times (or in a structured single agent pipeline)
        to generate the custom profiles, debates, Gherkin, Playwright, and quality characteristics.
        """
        system_instruction = """You are a software quality orchestration framework consisting of 8 collaborative AI clones.
Your task is to analyze the input survey and system name, and output a detailed simulation report in JSON format.

The JSON response MUST follow this exact structure:
{
  "domain": "string (e.g. ecommerce, expense, medical, or other)",
  "user_clones": [
    {
      "id": "string",
      "name": "string",
      "role": "string",
      "age": number,
      "tech_savviness": "string (Low/Med/High in Japanese)",
      "pain_points": ["string", "string"],
      "needs": "string"
    }
  ],
  "duplicate_clones": [
    {
      "id": "string",
      "base_id": "string",
      "name": "string",
      "role": "string",
      "age": number,
      "tech_savviness": "string",
      "reliability": number (0.0 to 1.0),
      "label": "string (e.g. 信頼性: 高/中/低)",
      "simulated_behavior": "string"
    }
  ],
  "debate_logs": [
    {
      "speaker": "string (e.g., QA1 (テスト設計担当), QA2 (UX品質担当), PM (プロジェクトマネージャー))",
      "avatar": "string (emoji)",
      "text": "string (Japanese conversation about requirements and user stories)"
    }
  ],
  "atdd_gherkin": "string (Gherkin test scenarios in Japanese)",
  "playwright_code": "string (Playwright test code script in JS/TS)",
  "feasibility_feedback": "string (Detailed assessment of test automation feasibility in Japanese)",
  "review_result": {
    "score": number (0 to 100),
    "status": "string (合格/改善要求あり)",
    "details": "string (Review details of specs vs ATDD in Japanese)"
  },
  "director_summary": "string (Overall report summary by the General Director in Japanese)",
  "quality_metrics": {
    "functional_suitability": number (0 to 100),
    "performance_efficiency": number (0 to 100),
    "compatibility": number (0 to 100),
    "usability": number (0 to 100),
    "reliability": number (0 to 100),
    "security": number (0 to 100),
    "maintainability": number (0 to 100),
    "portability": number (0 to 100)
  }
}

Ensure the content is detailed, creative, realistic, and fully tailored to the user's system and survey input.
"""

        prompt = f"""System Name: {system_name}
Real User Survey Input: {survey_input}

Please perform the agent pipeline simulation and generate the JSON output:"""

        try:
            if provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": system_instruction},
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.2
                    }
                }
                
                response = httpx.post(url, json=data, headers=headers, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                text_clean = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
                text_clean = re.sub(r"\s*```$", "", text_clean)
                parsed = json.loads(text_clean.strip())
                return parsed
                
            elif provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "model": model_name if model_name else "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
                response = httpx.post(url, json=data, headers=headers, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                text = result["choices"][0]["message"]["content"]
                parsed = json.loads(text)
                return parsed

            elif provider == "anthropic":
                url = "https://api.anthropic.com/v1/messages"
                headers = {
                    "content-type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                }
                data = {
                    "model": model_name if model_name else "claude-3-5-sonnet-20241022",
                    "max_tokens": 8000,
                    "system": system_instruction,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                response = httpx.post(url, json=data, headers=headers, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                text = result["content"][0]["text"]
                parsed = json.loads(text)
                return parsed

            else:
                return self._run_mock_simulation(survey_input, system_name)

        except Exception as e:
            mock_res = self._run_mock_simulation(survey_input, system_name)
            mock_res["director_summary"] = f"【注意: API呼び出しでエラーが発生したため、シミュレーションモードで実行されました (エラー詳細: {str(e)})】\n\n" + mock_res["director_summary"]
            return mock_res

    def run_periodic_review(self, spec_text: str, atdd_gherkin: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the periodic reviewer clone on a specification text vs the ATDD Gherkin.
        Supports both mock and live API.
        """
        api_key = settings.get("apiKey", "")
        provider = settings.get("provider", "mock")
        model_name = settings.get("model", "gemini-2.5-flash")

        if not api_key or provider == "mock":
            if "既存システム仕様" in spec_text or "plans.html" in spec_text or "フィルター" in spec_text and "存在しない" in spec_text:
                score = 35
                status = "改善要求あり (不適合)"
                details = """【既存サイト仕様レビュー結果 (不適合判定)】

既存の宿泊プラン一覧画面 (plans.html) の仕様と、上田様の要望に基づき策定したATDD基準（Given-When-Then）を照合しました。

■ 判定結果: 不適合 (適合度: 35%)

■ 不適合（ギャップ）の詳細:
1. 【重要項目】宿泊プラン一覧画面での日付フィルター機能の欠如:
   - ATDDの「Given: 日付に '2026/07/10' を指定している」「When: '空室のあるプランを検索' ボタンを押す」に対応する要素 (#checkin-date および #search-vacant-btn) が画面上に定義されていません。
2. 【重要項目】空室プランのみの絞り込み表示ロジックの欠如:
   - ATDDの「Then: 空室があるプランのみが一覧に表示される」に対応する、フロントエンドとPMS(在庫管理)のAPI連動処理が設計に盛り込まれていません。

■ 改善推奨項目:
- plans.html 画面上部に日付セレクト・チェックイン日入力用のフォームを追加し、空室のあるプランのみを表示する画面遷移フローを仕様に追加してください。"""
            else:
                score = 90
                status = "ATDD準拠 (合格)"
                details = f"【要件定義書・基本設計書レビュー結果 (モック判定)】\n\n入力された仕様書は、指定されたATDD基準に概ね適合しています (適合度: {score}%)。\n\n詳細分析:\n- シナリオに定義された「Given-When-Then」の主要なステップが設計書上の遷移プロセスと整合しています。\n- エラー時の例外ハンドリング仕様について、一部言及が薄い箇所がありますが、基本フローは担保されています。"
            return {
                "score": score,
                "status": status,
                "details": details
            }

        system_instruction = """You are the ATDD Periodic Reviewer Clone. 
Your task is to analyze the user's provided specification text against the target ATDD Gherkin scenarios.
Determine the compliance score (0-100), the status ("ATDD準拠 (合格)" or "改善要求あり (再確認)"), and write a detailed constructive feedback report in Japanese explaining the matched features and any omissions/violations.

Output a JSON response with this exact structure:
{
  "score": number,
  "status": "string",
  "details": "string"
}
"""
        prompt = f"""--- TARGET ATDD GHERKIN ---
{atdd_gherkin}

--- SUPPLIED SPECIFICATION TEXT ---
{spec_text}

Analyze and review the specification. Output JSON only:"""

        try:
            if provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": system_instruction},
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.2
                    }
                }
                response = httpx.post(url, json=data, headers=headers, timeout=60.0)
                response.raise_for_status()
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                text_clean = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
                text_clean = re.sub(r"\s*```$", "", text_clean)
                return json.loads(text_clean.strip())
            elif provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "model": model_name if model_name else "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
                response = httpx.post(url, json=data, headers=headers, timeout=60.0)
                response.raise_for_status()
                return json.loads(response.json()["choices"][0]["message"]["content"])
            elif provider == "anthropic":
                url = "https://api.anthropic.com/v1/messages"
                headers = {
                    "content-type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                }
                data = {
                    "model": model_name if model_name else "claude-3-5-sonnet-20241022",
                    "max_tokens": 4000,
                    "system": system_instruction,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                response = httpx.post(url, json=data, headers=headers, timeout=60.0)
                response.raise_for_status()
                return json.loads(response.json()["content"][0]["text"])
        except Exception as e:
            return {
                "score": 50,
                "status": "エラーにより判定不能",
                "details": f"API実行エラーにより自動レビューに失敗しました。詳細: {str(e)}"
            }
