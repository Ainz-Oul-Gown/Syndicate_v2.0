import re

with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

google_method = """                {/* Method 4: Google Account [B-Tier] */}
                <div className="relative group bg-slate-900/60 border border-slate-900 hover:border-rose-500/30 p-4.5 rounded-2xl text-left transition duration-300">
                  <div className="flex justify-between items-start">
                    <div className="flex gap-3">
                      <div className="w-10 h-10 bg-slate-800 rounded-xl flex items-center justify-center shrink-0 border border-slate-700 shadow-inner group-hover:bg-rose-500/10 group-hover:border-rose-500/20 transition">
                        <Chrome className="w-5 h-5 text-rose-400" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-bold text-slate-200 text-sm">Google Account</h3>
                          <span className="text-[8px] font-extrabold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">B-КЛАСС</span>
                        </div>
                        <p className="text-slate-400 text-[11px] mt-1 leading-relaxed">Быстрый вход через OAuth. Ключи шифруются по ID профиля Google.</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => showMethodInfo('google')}
                      className="p-1.5 text-slate-500 hover:text-slate-300 transition shrink-0 cursor-pointer"
                      title="Описание метода"
                    >
                      <Info className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <button 
                      onClick={() => { hapticImpact("selection"); setGoogleAction('login'); setViewMode('google_auth'); }}
                      className="flex-1 py-2 px-3 bg-slate-800 hover:bg-slate-750 text-slate-200 font-semibold text-xs rounded-xl transition"
                    >
                      Войти
                    </button>
                    <button 
                      onClick={() => { hapticImpact("selection"); setGoogleAction('register'); setGoogleName(''); setGoogleInvite(''); setErrorMessage(null); setViewMode('google_auth'); }}
                      className="flex-1 py-2 px-3 bg-rose-500/20 border border-rose-500/30 hover:bg-rose-500/30 text-rose-300 font-semibold text-xs rounded-xl transition"
                    >
                      Регистрация
                    </button>
                  </div>
                </div>

"""

if "Method 4: Google Account" not in content:
    content = content.replace("{/* Method 5: Email", google_method + "                {/* Method 5: Email")

google_auth_screen = """          {/* Google Auth Screen */}
          {viewMode === 'google_auth' && (
            <div className="flex flex-col items-center w-full text-left animate-fade-in">
              <button 
                onClick={() => { hapticImpact("selection"); setViewMode('alternative'); setErrorMessage(null); }}
                className="self-start flex items-center gap-2 text-xs text-slate-400 hover:text-slate-200 mb-6 transition cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" /> Назад
              </button>

              <h2 className="text-xl font-bold font-display text-slate-100 mb-2">
                {googleAction === 'register' ? 'Регистрация Google' : 'Вход через Google'}
              </h2>
              <p className="text-slate-400 text-xs mb-6 leading-relaxed">
                {googleAction === 'register' 
                  ? 'Введите ваши данные для регистрации в сети Syndicate. Мы привяжем крипто-ключи к вашему Google ID.' 
                  : 'Войдите с помощью привязанного Google аккаунта.'}
              </p>

              <div className="w-full flex flex-col gap-3.5 mb-6">
                {googleAction === 'register' && (
                  <>
                    <div className="flex flex-col gap-1">
                      <label className="text-[10px] font-bold font-mono text-slate-500 uppercase tracking-widest pl-1">Ваше Имя в Синдикате</label>
                      <div className="relative">
                        <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input 
                          type="text" 
                          placeholder="Имя для профиля" 
                          value={googleName}
                          onChange={(e) => setGoogleName(e.target.value)}
                          className="w-full bg-slate-900 border border-slate-850 focus:border-primary/60 outline-none rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 transition"
                        />
                      </div>
                    </div>

                    <div className="flex flex-col gap-1">
                      <label className="text-[10px] font-bold font-mono text-slate-500 uppercase tracking-widest pl-1">Код приглашения (Invite Code)</label>
                      <div className="relative">
                        <ShieldCheck className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input 
                          type="text" 
                          placeholder="XXX-YYY-ZZZ" 
                          value={googleInvite}
                          onChange={(e) => setGoogleInvite(e.target.value)}
                          className="w-full bg-slate-900 border border-slate-850 focus:border-primary/60 outline-none rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 transition font-mono uppercase"
                        />
                      </div>
                    </div>
                  </>
                )}
              </div>

              <button 
                onClick={handleRealGoogleSignIn}
                disabled={isSubmitting}
                className="w-full bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 py-3.5 text-white font-bold rounded-xl transition text-xs flex items-center justify-center gap-2 shadow-lg shadow-rose-500/20"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Chrome className="w-4 h-4" />}
                {isSubmitting ? 'Обработка...' : 'Продолжить через Google'}
              </button>
            </div>
          )}

"""

if "{/* Google Auth Screen */}" not in content:
    content = content.replace("{/* Telegram OTP Login / Register Screen */}", google_auth_screen + "          {/* Telegram OTP Login / Register Screen */}")

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
