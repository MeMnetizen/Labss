import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import filtfilt, iirfilter


def interactive_signal():
    initialAmplitude = 1.0
    initialFrequency = 1.0
    initialPhase = 0.0
    initialNoiseMean = 0.0
    initialNoiseCovariance = 0.1
    initialCutoffFrequency = 1.0

    t = np.arange(0.0, 10.0, 0.01)
    Fs = len(t) / (t[-1] - t[0])

    def generateHarmonic(A, f, phi):
        return A * np.sin(2 * np.pi * f * t + phi)

    def generateNoise(mean, cov):
        return np.random.normal(mean, np.sqrt(cov), size=len(t))

    def applyLowPassFilter(sig, cutoff):
        b, a = iirfilter(5, cutoff / (0.5 * Fs), btype='low', ftype='butter')
        return filtfilt(b, a, sig)

    fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    plt.subplots_adjust(left=0.12, bottom=0.38, right=0.85, hspace=0.4)

    axs[0].set_title('Гармоніка з шумом')
    axs[1].set_title('Низькочастотний фільтр')
    for ax in axs:
        ax.grid(True);
        ax.set_xlabel('Час, с');
        ax.set_ylabel('Амплітуда')

    clean_line, = axs[0].plot(t, generateHarmonic(initialAmplitude, initialFrequency, initialPhase),
                              color='blue', linewidth=2)
    noise_cache = generateNoise(initialNoiseMean, initialNoiseCovariance)
    noisy_line, = axs[0].plot(t, generateHarmonic(initialAmplitude, initialFrequency, initialPhase) + noise_cache,
                              color='red', linestyle='--', linewidth=1.5)
    noisy_line.set_visible(False)

    filtered_line, = axs[1].plot(t, generateHarmonic(initialAmplitude, initialFrequency, initialPhase),
                                 color='green', linewidth=2)

    widget_bg = '#EEE'
    ax_amp = plt.axes([0.12, 0.28, 0.6, 0.03], facecolor=widget_bg)
    ax_freq = plt.axes([0.12, 0.24, 0.6, 0.03], facecolor=widget_bg)
    ax_phase = plt.axes([0.12, 0.20, 0.6, 0.03], facecolor=widget_bg)
    ax_nmean = plt.axes([0.12, 0.16, 0.6, 0.03], facecolor=widget_bg)
    ax_ncov = plt.axes([0.12, 0.12, 0.6, 0.03], facecolor=widget_bg)
    ax_cut = plt.axes([0.12, 0.08, 0.6, 0.03], facecolor=widget_bg)
    ax_cb = plt.axes([0.76, 0.12, 0.12, 0.12], facecolor=widget_bg)
    ax_btn = plt.axes([0.76, 0.05, 0.12, 0.04], facecolor=widget_bg)

    s_amp = Slider(ax_amp, 'Амплітуда', 0.1, 10.0, valinit=initialAmplitude)
    s_freq = Slider(ax_freq, 'Частота (Hz)', 0.1, 10.0, valinit=initialFrequency)
    s_phase = Slider(ax_phase, 'Фазовий зсув (rad)', 0.0, 2 * np.pi, valinit=initialPhase)
    s_nmean = Slider(ax_nmean, 'Середнє шуму', -1.0, 1.0, valinit=initialNoiseMean)
    s_ncov = Slider(ax_ncov, 'Дисперсія шуму', 0.0, 1.0, valinit=initialNoiseCovariance)
    s_cut = Slider(ax_cut, 'Частота зрізу', 0.1, 5.0, valinit=initialCutoffFrequency)

    cb = CheckButtons(ax_cb, ['Шум'], [False])
    btn = Button(ax_btn, 'Reset')

    def redraw():
        A, f, phi = s_amp.val, s_freq.val, s_phase.val
        m, cov = s_nmean.val, s_ncov.val
        cut = s_cut.val
        show = cb.get_status()[0]

        clean = generateHarmonic(A, f, phi)
        clean_line.set_ydata(clean)

        noisy = clean + noise_cache if show else clean
        noisy_line.set_ydata(noisy)
        noisy_line.set_visible(show)

        filtered = applyLowPassFilter(noisy, cut)
        filtered_line.set_ydata(filtered)

        fig.canvas.draw_idle()

    def on_noise_change(val):
        nonlocal noise_cache
        noise_cache = generateNoise(s_nmean.val, s_ncov.val)
        redraw()

    def on_param_change(val):
        redraw()

    for slider in (s_nmean, s_ncov):
        slider.on_changed(on_noise_change)

    for slider in (s_amp, s_freq, s_phase, s_cut):
        slider.on_changed(on_param_change)

    cb.on_clicked(lambda _: redraw())
    btn.on_clicked(lambda _: (
        [w.reset() for w in (s_amp, s_freq, s_phase, s_nmean, s_ncov, s_cut)],
        redraw()
    ))

    plt.show()


interactive_signal()
