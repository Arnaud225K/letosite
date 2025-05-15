// ========================================
// START: Contenu de sliders.txt (Swiper JS Library + Initialisation)
// ========================================
(() => { // <--- DÉBUT de l'IIFE Swiper
    "use strict";
    function e(e) {
        return null !== e && "object" == typeof e && "constructor" in e && e.constructor === Object;
    }
    function t(s, i) {
        void 0 === s && (s = {}), void 0 === i && (i = {});
        const r = ["__proto__", "constructor", "prototype"];
        Object.keys(i)
            .filter((e) => r.indexOf(e) < 0)
            .forEach((r) => {
                void 0 === s[r] ? (s[r] = i[r]) : e(i[r]) && e(s[r]) && Object.keys(i[r]).length > 0 && t(s[r], i[r]);
            });
    }
    const s = {
        body: {},
        addEventListener() {},
        removeEventListener() {},
        activeElement: { blur() {}, nodeName: "" },
        querySelector: () => null,
        querySelectorAll: () => [],
        getElementById: () => null,
        createEvent: () => ({ initEvent() {} }),
        createElement: () => ({ children: [], childNodes: [], style: {}, setAttribute() {}, getElementsByTagName: () => [] }),
        createElementNS: () => ({}),
        importNode: () => null,
        location: { hash: "", host: "", hostname: "", href: "", origin: "", pathname: "", protocol: "", search: "" },
    };
    function i() {
        const e = "undefined" != typeof document ? document : {};
        return t(e, s), e;
    }
    const r = {
        document: s,
        navigator: { userAgent: "" },
        location: { hash: "", host: "", hostname: "", href: "", origin: "", pathname: "", protocol: "", search: "" },
        history: { replaceState() {}, pushState() {}, go() {}, back() {} },
        CustomEvent: function () {
            return this;
        },
        addEventListener() {},
        removeEventListener() {},
        getComputedStyle: () => ({ getPropertyValue: () => "" }),
        Image() {},
        Date() {},
        screen: {},
        setTimeout() {},
        clearTimeout() {},
        matchMedia: () => ({}),
        requestAnimationFrame: (e) => ("undefined" == typeof setTimeout ? (e(), null) : setTimeout(e, 0)),
        cancelAnimationFrame(e) {
            "undefined" != typeof setTimeout && clearTimeout(e);
        },
    };
    function a() {
        const e = "undefined" != typeof window ? window : {};
        return t(e, r), e;
    }
    function n(e) {
        return (
            void 0 === e && (e = ""),
            e
                .trim()
                .split(" ")
                .filter((e) => !!e.trim())
        );
    }
    function l(e, t) {
        return void 0 === t && (t = 0), setTimeout(e, t);
    }
    function o() {
        return Date.now();
    }
    function d(e) {
        return "object" == typeof e && null !== e && e.constructor && "Object" === Object.prototype.toString.call(e).slice(8, -1);
    }
    function c() {
        const e = Object(arguments.length <= 0 ? void 0 : arguments[0]),
            t = ["__proto__", "constructor", "prototype"];
        for (let i = 1; i < arguments.length; i += 1) {
            const r = i < 0 || arguments.length <= i ? void 0 : arguments[i];
            if (null != r && ((s = r), !("undefined" != typeof window && void 0 !== window.HTMLElement ? s instanceof HTMLElement : s && (1 === s.nodeType || 11 === s.nodeType)))) {
                const s = Object.keys(Object(r)).filter((e) => t.indexOf(e) < 0);
                for (let t = 0, i = s.length; t < i; t += 1) {
                    const i = s[t],
                        a = Object.getOwnPropertyDescriptor(r, i);
                    void 0 !== a && a.enumerable && (d(e[i]) && d(r[i]) ? (r[i].__swiper__ ? (e[i] = r[i]) : c(e[i], r[i])) : !d(e[i]) && d(r[i]) ? ((e[i] = {}), r[i].__swiper__ ? (e[i] = r[i]) : c(e[i], r[i])) : (e[i] = r[i]));
                }
            }
        }
        var s;
        return e;
    }
    function p(e, t, s) {
        e.style.setProperty(t, s);
    }
    function u(e) {
        let { swiper: t, targetPosition: s, side: i } = e;
        const r = a(),
            n = -t.translate;
        let l,
            o = null;
        const d = t.params.speed;
        (t.wrapperEl.style.scrollSnapType = "none"), r.cancelAnimationFrame(t.cssModeFrameID);
        const c = s > n ? "next" : "prev",
            p = (e, t) => ("next" === c && e >= t) || ("prev" === c && e <= t),
            u = () => {
                (l = new Date().getTime()), null === o && (o = l);
                const e = Math.max(Math.min((l - o) / d, 1), 0),
                    a = 0.5 - Math.cos(e * Math.PI) / 2;
                let c = n + a * (s - n);
                if ((p(c, s) && (c = s), t.wrapperEl.scrollTo({ [i]: c }), p(c, s)))
                    return (
                        (t.wrapperEl.style.overflow = "hidden"),
                        (t.wrapperEl.style.scrollSnapType = ""),
                        setTimeout(() => {
                            (t.wrapperEl.style.overflow = ""), t.wrapperEl.scrollTo({ [i]: c });
                        }),
                        void r.cancelAnimationFrame(t.cssModeFrameID)
                    );
                t.cssModeFrameID = r.requestAnimationFrame(u);
            };
        u();
    }
    function m(e, t) {
        void 0 === t && (t = "");
        const s = a(),
            i = [...e.children];
        return s.HTMLSlotElement && e instanceof HTMLSlotElement && i.push(...e.assignedElements()), t ? i.filter((e) => e.matches(t)) : i;
    }
    function f(e) {
        try {
            return void console.warn(e);
        } catch (e) {}
    }
    function h(e, t) {
        void 0 === t && (t = []);
        const s = document.createElement(e);
        return s.classList.add(...(Array.isArray(t) ? t : n(t))), s;
    }
    function v(e, t) {
        return a().getComputedStyle(e, null).getPropertyValue(t);
    }
    function g(e) {
        let t,
            s = e;
        if (s) {
            for (t = 0; null !== (s = s.previousSibling); ) 1 === s.nodeType && (t += 1);
            return t;
        }
    }
    function w(e, t, s) {
        const i = a();
        return s
            ? e["width" === t ? "offsetWidth" : "offsetHeight"] +
                  parseFloat(i.getComputedStyle(e, null).getPropertyValue("width" === t ? "margin-right" : "margin-top")) +
                  parseFloat(i.getComputedStyle(e, null).getPropertyValue("width" === t ? "margin-left" : "margin-bottom"))
            : e.offsetWidth;
    }
    function b(e) {
        return (Array.isArray(e) ? e : [e]).filter((e) => !!e);
    }
    let S, T, y;
    function E() {
        return (
            S ||
                (S = (function () {
                    const e = a(),
                        t = i();
                    return { smoothScroll: t.documentElement && t.documentElement.style && "scrollBehavior" in t.documentElement.style, touch: !!("ontouchstart" in e || (e.DocumentTouch && t instanceof e.DocumentTouch)) };
                })()),
            S
        );
    }
    function x(e) {
        return (
            void 0 === e && (e = {}),
            T ||
                (T = (function (e) {
                    let { userAgent: t } = void 0 === e ? {} : e;
                    const s = E(),
                        i = a(),
                        r = i.navigator.platform,
                        n = t || i.navigator.userAgent,
                        l = { ios: !1, android: !1 },
                        o = i.screen.width,
                        d = i.screen.height,
                        c = n.match(/(Android);?[\s\/]+([\d.]+)?/);
                    let p = n.match(/(iPad).*OS\s([\d_]+)/);
                    const u = n.match(/(iPod)(.*OS\s([\d_]+))?/),
                        m = !p && n.match(/(iPhone\sOS|iOS)\s([\d_]+)/),
                        f = "Win32" === r;
                    let h = "MacIntel" === r;
                    return (
                        !p &&
                            h &&
                            s.touch &&
                            ["1024x1366", "1366x1024", "834x1194", "1194x834", "834x1112", "1112x834", "768x1024", "1024x768", "820x1180", "1180x820", "810x1080", "1080x810"].indexOf(`${o}x${d}`) >= 0 &&
                            ((p = n.match(/(Version)\/([\d.]+)/)), p || (p = [0, 1, "13_0_0"]), (h = !1)),
                        c && !f && ((l.os = "android"), (l.android = !0)),
                        (p || m || u) && ((l.os = "ios"), (l.ios = !0)),
                        l
                    );
                })(e)),
            T
        );
    }
    function C() {
        return (
            y ||
                (y = (function () {
                    const e = a(),
                        t = x();
                    let s = !1;
                    function i() {
                        const t = e.navigator.userAgent.toLowerCase();
                        return t.indexOf("safari") >= 0 && t.indexOf("chrome") < 0 && t.indexOf("android") < 0;
                    }
                    if (i()) {
                        const t = String(e.navigator.userAgent);
                        if (t.includes("Version/")) {
                            const [e, i] = t
                                .split("Version/")[1]
                                .split(" ")[0]
                                .split(".")
                                .map((e) => Number(e));
                            s = e < 16 || (16 === e && i < 2);
                        }
                    }
                    const r = /(iPhone|iPod|iPad).*AppleWebKit(?!.*Safari)/i.test(e.navigator.userAgent),
                        n = i();
                    return { isSafari: s || n, needPerspectiveFix: s, need3dFix: n || (r && t.ios), isWebView: r };
                })()),
            y
        );
    }
    var M = {
        on(e, t, s) {
            const i = this;
            if (!i.eventsListeners || i.destroyed) return i;
            if ("function" != typeof t) return i;
            const r = s ? "unshift" : "push";
            return (
                e.split(" ").forEach((e) => {
                    i.eventsListeners[e] || (i.eventsListeners[e] = []), i.eventsListeners[e][r](t);
                }),
                i
            );
        },
        once(e, t, s) {
            const i = this;
            if (!i.eventsListeners || i.destroyed) return i;
            if ("function" != typeof t) return i;
            function r() {
                i.off(e, r), r.__emitterProxy && delete r.__emitterProxy;
                for (var s = arguments.length, a = new Array(s), n = 0; n < s; n++) a[n] = arguments[n];
                t.apply(i, a);
            }
            return (r.__emitterProxy = t), i.on(e, r, s);
        },
        onAny(e, t) {
            const s = this;
            if (!s.eventsListeners || s.destroyed) return s;
            if ("function" != typeof e) return s;
            const i = t ? "unshift" : "push";
            return s.eventsAnyListeners.indexOf(e) < 0 && s.eventsAnyListeners[i](e), s;
        },
        offAny(e) {
            const t = this;
            if (!t.eventsListeners || t.destroyed) return t;
            if (!t.eventsAnyListeners) return t;
            const s = t.eventsAnyListeners.indexOf(e);
            return s >= 0 && t.eventsAnyListeners.splice(s, 1), t;
        },
        off(e, t) {
            const s = this;
            return !s.eventsListeners || s.destroyed
                ? s
                : s.eventsListeners
                ? (e.split(" ").forEach((e) => {
                      void 0 === t
                          ? (s.eventsListeners[e] = [])
                          : s.eventsListeners[e] &&
                            s.eventsListeners[e].forEach((i, r) => {
                                (i === t || (i.__emitterProxy && i.__emitterProxy === t)) && s.eventsListeners[e].splice(r, 1);
                            });
                  }),
                  s)
                : s;
        },
        emit() {
            const e = this;
            if (!e.eventsListeners || e.destroyed) return e;
            if (!e.eventsListeners) return e;
            let t, s, i;
            for (var r = arguments.length, a = new Array(r), n = 0; n < r; n++) a[n] = arguments[n];
            return (
                "string" == typeof a[0] || Array.isArray(a[0]) ? ((t = a[0]), (s = a.slice(1, a.length)), (i = e)) : ((t = a[0].events), (s = a[0].data), (i = a[0].context || e)),
                s.unshift(i),
                (Array.isArray(t) ? t : t.split(" ")).forEach((t) => {
                    e.eventsAnyListeners &&
                        e.eventsAnyListeners.length &&
                        e.eventsAnyListeners.forEach((e) => {
                            e.apply(i, [t, ...s]);
                        }),
                        e.eventsListeners &&
                            e.eventsListeners[t] &&
                            e.eventsListeners[t].forEach((e) => {
                                e.apply(i, s);
                            });
                }),
                e
            );
        },
    };
    const P = (e, t, s) => {
            t && !e.classList.contains(s) ? e.classList.add(s) : !t && e.classList.contains(s) && e.classList.remove(s);
        },
        L = (e, t, s) => {
            t && !e.classList.contains(s) ? e.classList.add(s) : !t && e.classList.contains(s) && e.classList.remove(s);
        },
        k = (e, t) => {
            if (!e || e.destroyed || !e.params) return;
            const s = t.closest(e.isElement ? "swiper-slide" : `.${e.params.slideClass}`);
            if (s) {
                let t = s.querySelector(`.${e.params.lazyPreloaderClass}`);
                !t &&
                    e.isElement &&
                    (s.shadowRoot
                        ? (t = s.shadowRoot.querySelector(`.${e.params.lazyPreloaderClass}`))
                        : requestAnimationFrame(() => {
                              s.shadowRoot && ((t = s.shadowRoot.querySelector(`.${e.params.lazyPreloaderClass}`)), t && t.remove());
                          })),
                    t && t.remove();
            }
        },
        I = (e, t) => {
            if (!e.slides[t]) return;
            const s = e.slides[t].querySelector('[loading="lazy"]');
            s && s.removeAttribute("loading");
        },
        O = (e) => {
            if (!e || e.destroyed || !e.params) return;
            let t = e.params.lazyPreloadPrevNext;
            const s = e.slides.length;
            if (!s || !t || t < 0) return;
            t = Math.min(t, s);
            const i = "auto" === e.params.slidesPerView ? e.slidesPerViewDynamic() : Math.ceil(e.params.slidesPerView),
                r = e.activeIndex;
            if (e.params.grid && e.params.grid.rows > 1) {
                const s = r,
                    a = [s - t];
                return (
                    a.push(...Array.from({ length: t }).map((e, t) => s + i + t)),
                    void e.slides.forEach((t, s) => {
                        a.includes(t.column) && I(e, s);
                    })
                );
            }
            const a = r + i - 1;
            if (e.params.rewind || e.params.loop)
                for (let i = r - t; i <= a + t; i += 1) {
                    const t = ((i % s) + s) % s;
                    (t < r || t > a) && I(e, t);
                }
            else for (let i = Math.max(r - t, 0); i <= Math.min(a + t, s - 1); i += 1) i !== r && (i > a || i < r) && I(e, i);
        };
    var z = {
        updateSize: function () {
            const e = this;
            let t, s;
            const i = e.el;
            (t = void 0 !== e.params.width && null !== e.params.width ? e.params.width : i.clientWidth),
                (s = void 0 !== e.params.height && null !== e.params.height ? e.params.height : i.clientHeight),
                (0 === t && e.isHorizontal()) ||
                    (0 === s && e.isVertical()) ||
                    ((t = t - parseInt(v(i, "padding-left") || 0, 10) - parseInt(v(i, "padding-right") || 0, 10)),
                    (s = s - parseInt(v(i, "padding-top") || 0, 10) - parseInt(v(i, "padding-bottom") || 0, 10)),
                    Number.isNaN(t) && (t = 0),
                    Number.isNaN(s) && (s = 0),
                    Object.assign(e, { width: t, height: s, size: e.isHorizontal() ? t : s }));
        },
        updateSlides: function () {
            const e = this;
            function t(t, s) {
                return parseFloat(t.getPropertyValue(e.getDirectionLabel(s)) || 0);
            }
            const s = e.params,
                { wrapperEl: i, slidesEl: r, size: a, rtlTranslate: n, wrongRTL: l } = e,
                o = e.virtual && s.virtual.enabled,
                d = o ? e.virtual.slides.length : e.slides.length,
                c = m(r, `.${e.params.slideClass}, swiper-slide`),
                u = o ? e.virtual.slides.length : c.length;
            let f = [];
            const h = [],
                g = [];
            let b = s.slidesOffsetBefore;
            "function" == typeof b && (b = s.slidesOffsetBefore.call(e));
            let S = s.slidesOffsetAfter;
            "function" == typeof S && (S = s.slidesOffsetAfter.call(e));
            const T = e.snapGrid.length,
                y = e.slidesGrid.length;
            let E = s.spaceBetween,
                x = -b,
                C = 0,
                M = 0;
            if (void 0 === a) return;
            "string" == typeof E && E.indexOf("%") >= 0 ? (E = (parseFloat(E.replace("%", "")) / 100) * a) : "string" == typeof E && (E = parseFloat(E)),
                (e.virtualSize = -E),
                c.forEach((e) => {
                    n ? (e.style.marginLeft = "") : (e.style.marginRight = ""), (e.style.marginBottom = ""), (e.style.marginTop = "");
                }),
                s.centeredSlides && s.cssMode && (p(i, "--swiper-centered-offset-before", ""), p(i, "--swiper-centered-offset-after", ""));
            const P = s.grid && s.grid.rows > 1 && e.grid;
            let L;
            P ? e.grid.initSlides(c) : e.grid && e.grid.unsetSlides();
            const k = "auto" === s.slidesPerView && s.breakpoints && Object.keys(s.breakpoints).filter((e) => void 0 !== s.breakpoints[e].slidesPerView).length > 0;
            for (let i = 0; i < u; i += 1) {
                let r;
                if (((L = 0), c[i] && (r = c[i]), P && e.grid.updateSlide(i, r, c), !c[i] || "none" !== v(r, "display"))) {
                    if ("auto" === s.slidesPerView) {
                        k && (c[i].style[e.getDirectionLabel("width")] = "");
                        const a = getComputedStyle(r),
                            n = r.style.transform,
                            l = r.style.webkitTransform;
                        if ((n && (r.style.transform = "none"), l && (r.style.webkitTransform = "none"), s.roundLengths)) L = e.isHorizontal() ? w(r, "width", !0) : w(r, "height", !0);
                        else {
                            const e = t(a, "width"),
                                s = t(a, "padding-left"),
                                i = t(a, "padding-right"),
                                n = t(a, "margin-left"),
                                l = t(a, "margin-right"),
                                o = a.getPropertyValue("box-sizing");
                            if (o && "border-box" === o) L = e + n + l;
                            else {
                                const { clientWidth: t, offsetWidth: a } = r;
                                L = e + s + i + n + l + (a - t);
                            }
                        }
                        n && (r.style.transform = n), l && (r.style.webkitTransform = l), s.roundLengths && (L = Math.floor(L));
                    } else (L = (a - (s.slidesPerView - 1) * E) / s.slidesPerView), s.roundLengths && (L = Math.floor(L)), c[i] && (c[i].style[e.getDirectionLabel("width")] = `${L}px`);
                    c[i] && (c[i].swiperSlideSize = L),
                        g.push(L),
                        s.centeredSlides
                            ? ((x = x + L / 2 + C / 2 + E),
                              0 === C && 0 !== i && (x = x - a / 2 - E),
                              0 === i && (x = x - a / 2 - E),
                              Math.abs(x) < 0.001 && (x = 0),
                              s.roundLengths && (x = Math.floor(x)),
                              M % s.slidesPerGroup == 0 && f.push(x),
                              h.push(x))
                            : (s.roundLengths && (x = Math.floor(x)), (M - Math.min(e.params.slidesPerGroupSkip, M)) % e.params.slidesPerGroup == 0 && f.push(x), h.push(x), (x = x + L + E)),
                        (e.virtualSize += L + E),
                        (C = L),
                        (M += 1);
                }
            }
            if (
                ((e.virtualSize = Math.max(e.virtualSize, a) + S),
                n && l && ("slide" === s.effect || "coverflow" === s.effect) && (i.style.width = `${e.virtualSize + E}px`),
                s.setWrapperSize && (i.style[e.getDirectionLabel("width")] = `${e.virtualSize + E}px`),
                P && e.grid.updateWrapperSize(L, f),
                !s.centeredSlides)
            ) {
                const t = [];
                for (let i = 0; i < f.length; i += 1) {
                    let r = f[i];
                    s.roundLengths && (r = Math.floor(r)), f[i] <= e.virtualSize - a && t.push(r);
                }
                (f = t), Math.floor(e.virtualSize - a) - Math.floor(f[f.length - 1]) > 1 && f.push(e.virtualSize - a);
            }
            if (o && s.loop) {
                const t = g[0] + E;
                if (s.slidesPerGroup > 1) {
                    const i = Math.ceil((e.virtual.slidesBefore + e.virtual.slidesAfter) / s.slidesPerGroup),
                        r = t * s.slidesPerGroup;
                    for (let e = 0; e < i; e += 1) f.push(f[f.length - 1] + r);
                }
                for (let i = 0; i < e.virtual.slidesBefore + e.virtual.slidesAfter; i += 1) 1 === s.slidesPerGroup && f.push(f[f.length - 1] + t), h.push(h[h.length - 1] + t), (e.virtualSize += t);
            }
            if ((0 === f.length && (f = [0]), 0 !== E)) {
                const t = e.isHorizontal() && n ? "marginLeft" : e.getDirectionLabel("marginRight");
                c.filter((e, t) => !(s.cssMode && !s.loop) || t !== c.length - 1).forEach((e) => {
                    e.style[t] = `${E}px`;
                });
            }
            if (s.centeredSlides && s.centeredSlidesBounds) {
                let e = 0;
                g.forEach((t) => {
                    e += t + (E || 0);
                }),
                    (e -= E);
                const t = e > a ? e - a : 0;
                f = f.map((e) => (e <= 0 ? -b : e > t ? t + S : e));
            }
            if (s.centerInsufficientSlides) {
                let e = 0;
                g.forEach((t) => {
                    e += t + (E || 0);
                }),
                    (e -= E);
                const t = (s.slidesOffsetBefore || 0) + (s.slidesOffsetAfter || 0);
                if (e + t < a) {
                    const s = (a - e - t) / 2;
                    f.forEach((e, t) => {
                        f[t] = e - s;
                    }),
                        h.forEach((e, t) => {
                            h[t] = e + s;
                        });
                }
            }
            if ((Object.assign(e, { slides: c, snapGrid: f, slidesGrid: h, slidesSizesGrid: g }), s.centeredSlides && s.cssMode && !s.centeredSlidesBounds)) {
                p(i, "--swiper-centered-offset-before", -f[0] + "px"), p(i, "--swiper-centered-offset-after", e.size / 2 - g[g.length - 1] / 2 + "px");
                const t = -e.snapGrid[0],
                    s = -e.slidesGrid[0];
                (e.snapGrid = e.snapGrid.map((e) => e + t)), (e.slidesGrid = e.slidesGrid.map((e) => e + s));
            }
            if (
                (u !== d && e.emit("slidesLengthChange"),
                f.length !== T && (e.params.watchOverflow && e.checkOverflow(), e.emit("snapGridLengthChange")),
                h.length !== y && e.emit("slidesGridLengthChange"),
                s.watchSlidesProgress && e.updateSlidesOffset(),
                e.emit("slidesUpdated"),
                !(o || s.cssMode || ("slide" !== s.effect && "fade" !== s.effect)))
            ) {
                const t = `${s.containerModifierClass}backface-hidden`,
                    i = e.el.classList.contains(t);
                u <= s.maxBackfaceHiddenSlides ? i || e.el.classList.add(t) : i && e.el.classList.remove(t);
            }
        },
        updateAutoHeight: function (e) {
            const t = this,
                s = [],
                i = t.virtual && t.params.virtual.enabled;
            let r,
                a = 0;
            "number" == typeof e ? t.setTransition(e) : !0 === e && t.setTransition(t.params.speed);
            const n = (e) => (i ? t.slides[t.getSlideIndexByData(e)] : t.slides[e]);
            if ("auto" !== t.params.slidesPerView && t.params.slidesPerView > 1)
                if (t.params.centeredSlides)
                    (t.visibleSlides || []).forEach((e) => {
                        s.push(e);
                    });
                else
                    for (r = 0; r < Math.ceil(t.params.slidesPerView); r += 1) {
                        const e = t.activeIndex + r;
                        if (e > t.slides.length && !i) break;
                        s.push(n(e));
                    }
            else s.push(n(t.activeIndex));
            for (r = 0; r < s.length; r += 1)
                if (void 0 !== s[r]) {
                    const e = s[r].offsetHeight;
                    a = e > a ? e : a;
                }
            (a || 0 === a) && (t.wrapperEl.style.height = `${a}px`);
        },
        updateSlidesOffset: function () {
            const e = this,
                t = e.slides,
                s = e.isElement ? (e.isHorizontal() ? e.wrapperEl.offsetLeft : e.wrapperEl.offsetTop) : 0;
            for (let i = 0; i < t.length; i += 1) t[i].swiperSlideOffset = (e.isHorizontal() ? t[i].offsetLeft : t[i].offsetTop) - s - e.cssOverflowAdjustment();
        },
        updateSlidesProgress: function (e) {
            void 0 === e && (e = (this && this.translate) || 0);
            const t = this,
                s = t.params,
                { slides: i, rtlTranslate: r, snapGrid: a } = t;
            if (0 === i.length) return;
            void 0 === i[0].swiperSlideOffset && t.updateSlidesOffset();
            let n = -e;
            r && (n = e), (t.visibleSlidesIndexes = []), (t.visibleSlides = []);
            let l = s.spaceBetween;
            "string" == typeof l && l.indexOf("%") >= 0 ? (l = (parseFloat(l.replace("%", "")) / 100) * t.size) : "string" == typeof l && (l = parseFloat(l));
            for (let e = 0; e < i.length; e += 1) {
                const o = i[e];
                let d = o.swiperSlideOffset;
                s.cssMode && s.centeredSlides && (d -= i[0].swiperSlideOffset);
                const c = (n + (s.centeredSlides ? t.minTranslate() : 0) - d) / (o.swiperSlideSize + l),
                    p = (n - a[0] + (s.centeredSlides ? t.minTranslate() : 0) - d) / (o.swiperSlideSize + l),
                    u = -(n - d),
                    m = u + t.slidesSizesGrid[e],
                    f = u >= 0 && u <= t.size - t.slidesSizesGrid[e],
                    h = (u >= 0 && u < t.size - 1) || (m > 1 && m <= t.size) || (u <= 0 && m >= t.size);
                h && (t.visibleSlides.push(o), t.visibleSlidesIndexes.push(e)), P(o, h, s.slideVisibleClass), P(o, f, s.slideFullyVisibleClass), (o.progress = r ? -c : c), (o.originalProgress = r ? -p : p);
            }
        },
        updateProgress: function (e) {
            const t = this;
            if (void 0 === e) {
                const s = t.rtlTranslate ? -1 : 1;
                e = (t && t.translate && t.translate * s) || 0;
            }
            const s = t.params,
                i = t.maxTranslate() - t.minTranslate();
            let { progress: r, isBeginning: a, isEnd: n, progressLoop: l } = t;
            const o = a,
                d = n;
            if (0 === i) (r = 0), (a = !0), (n = !0);
            else {
                r = (e - t.minTranslate()) / i;
                const s = Math.abs(e - t.minTranslate()) < 1,
                    l = Math.abs(e - t.maxTranslate()) < 1;
                (a = s || r <= 0), (n = l || r >= 1), s && (r = 0), l && (r = 1);
            }
            if (s.loop) {
                const s = t.getSlideIndexByData(0),
                    i = t.getSlideIndexByData(t.slides.length - 1),
                    r = t.slidesGrid[s],
                    a = t.slidesGrid[i],
                    n = t.slidesGrid[t.slidesGrid.length - 1],
                    o = Math.abs(e);
                (l = o >= r ? (o - r) / n : (o + n - a) / n), l > 1 && (l -= 1);
            }
            Object.assign(t, { progress: r, progressLoop: l, isBeginning: a, isEnd: n }),
                (s.watchSlidesProgress || (s.centeredSlides && s.autoHeight)) && t.updateSlidesProgress(e),
                a && !o && t.emit("reachBeginning toEdge"),
                n && !d && t.emit("reachEnd toEdge"),
                ((o && !a) || (d && !n)) && t.emit("fromEdge"),
                t.emit("progress", r);
        },
        updateSlidesClasses: function () {
            const e = this,
                { slides: t, params: s, slidesEl: i, activeIndex: r } = e,
                a = e.virtual && s.virtual.enabled,
                n = e.grid && s.grid && s.grid.rows > 1,
                l = (e) => m(i, `.${s.slideClass}${e}, swiper-slide${e}`)[0];
            let o, d, c;
            if (a)
                if (s.loop) {
                    let t = r - e.virtual.slidesBefore;
                    t < 0 && (t = e.virtual.slides.length + t), t >= e.virtual.slides.length && (t -= e.virtual.slides.length), (o = l(`[data-swiper-slide-index="${t}"]`));
                } else o = l(`[data-swiper-slide-index="${r}"]`);
            else n ? ((o = t.find((e) => e.column === r)), (c = t.find((e) => e.column === r + 1)), (d = t.find((e) => e.column === r - 1))) : (o = t[r]);
            o &&
                (n ||
                    ((c = (function (e, t) {
                        const s = [];
                        for (; e.nextElementSibling; ) {
                            const i = e.nextElementSibling;
                            t ? i.matches(t) && s.push(i) : s.push(i), (e = i);
                        }
                        return s;
                    })(o, `.${s.slideClass}, swiper-slide`)[0]),
                    s.loop && !c && (c = t[0]),
                    (d = (function (e, t) {
                        const s = [];
                        for (; e.previousElementSibling; ) {
                            const i = e.previousElementSibling;
                            t ? i.matches(t) && s.push(i) : s.push(i), (e = i);
                        }
                        return s;
                    })(o, `.${s.slideClass}, swiper-slide`)[0]),
                    s.loop && 0 === !d && (d = t[t.length - 1]))),
                t.forEach((e) => {
                    L(e, e === o, s.slideActiveClass), L(e, e === c, s.slideNextClass), L(e, e === d, s.slidePrevClass);
                }),
                e.emitSlidesClasses();
        },
        updateActiveIndex: function (e) {
            const t = this,
                s = t.rtlTranslate ? t.translate : -t.translate,
                { snapGrid: i, params: r, activeIndex: a, realIndex: n, snapIndex: l } = t;
            let o,
                d = e;
            const c = (e) => {
                let s = e - t.virtual.slidesBefore;
                return s < 0 && (s = t.virtual.slides.length + s), s >= t.virtual.slides.length && (s -= t.virtual.slides.length), s;
            };
            if (
                (void 0 === d &&
                    (d = (function (e) {
                        const { slidesGrid: t, params: s } = e,
                            i = e.rtlTranslate ? e.translate : -e.translate;
                        let r;
                        for (let e = 0; e < t.length; e += 1) void 0 !== t[e + 1] ? (i >= t[e] && i < t[e + 1] - (t[e + 1] - t[e]) / 2 ? (r = e) : i >= t[e] && i < t[e + 1] && (r = e + 1)) : i >= t[e] && (r = e);
                        return s.normalizeSlideIndex && (r < 0 || void 0 === r) && (r = 0), r;
                    })(t)),
                i.indexOf(s) >= 0)
            )
                o = i.indexOf(s);
            else {
                const e = Math.min(r.slidesPerGroupSkip, d);
                o = e + Math.floor((d - e) / r.slidesPerGroup);
            }
            if ((o >= i.length && (o = i.length - 1), d === a && !t.params.loop)) return void (o !== l && ((t.snapIndex = o), t.emit("snapIndexChange")));
            if (d === a && t.params.loop && t.virtual && t.params.virtual.enabled) return void (t.realIndex = c(d));
            const p = t.grid && r.grid && r.grid.rows > 1;
            let u;
            if (t.virtual && r.virtual.enabled && r.loop) u = c(d);
            else if (p) {
                const e = t.slides.find((e) => e.column === d);
                let s = parseInt(e.getAttribute("data-swiper-slide-index"), 10);
                Number.isNaN(s) && (s = Math.max(t.slides.indexOf(e), 0)), (u = Math.floor(s / r.grid.rows));
            } else if (t.slides[d]) {
                const e = t.slides[d].getAttribute("data-swiper-slide-index");
                u = e ? parseInt(e, 10) : d;
            } else u = d;
            Object.assign(t, { previousSnapIndex: l, snapIndex: o, previousRealIndex: n, realIndex: u, previousIndex: a, activeIndex: d }),
                t.initialized && O(t),
                t.emit("activeIndexChange"),
                t.emit("snapIndexChange"),
                (t.initialized || t.params.runCallbacksOnInit) && (n !== u && t.emit("realIndexChange"), t.emit("slideChange"));
        },
        updateClickedSlide: function (e, t) {
            const s = this,
                i = s.params;
            let r = e.closest(`.${i.slideClass}, swiper-slide`);
            !r &&
                s.isElement &&
                t &&
                t.length > 1 &&
                t.includes(e) &&
                [...t.slice(t.indexOf(e) + 1, t.length)].forEach((e) => {
                    !r && e.matches && e.matches(`.${i.slideClass}, swiper-slide`) && (r = e);
                });
            let a,
                n = !1;
            if (r)
                for (let e = 0; e < s.slides.length; e += 1)
                    if (s.slides[e] === r) {
                        (n = !0), (a = e);
                        break;
                    }
            if (!r || !n) return (s.clickedSlide = void 0), void (s.clickedIndex = void 0);
            (s.clickedSlide = r),
                s.virtual && s.params.virtual.enabled ? (s.clickedIndex = parseInt(r.getAttribute("data-swiper-slide-index"), 10)) : (s.clickedIndex = a),
                i.slideToClickedSlide && void 0 !== s.clickedIndex && s.clickedIndex !== s.activeIndex && s.slideToClickedSlide();
        },
    };
    function A(e) {
        let { swiper: t, runCallbacks: s, direction: i, step: r } = e;
        const { activeIndex: a, previousIndex: n } = t;
        let l = i;
        if ((l || (l = a > n ? "next" : a < n ? "prev" : "reset"), t.emit(`transition${r}`), s && a !== n)) {
            if ("reset" === l) return void t.emit(`slideResetTransition${r}`);
            t.emit(`slideChangeTransition${r}`), "next" === l ? t.emit(`slideNextTransition${r}`) : t.emit(`slidePrevTransition${r}`);
        }
    }
    var D = {
            slideTo: function (e, t, s, i, r) {
                void 0 === e && (e = 0), void 0 === s && (s = !0), "string" == typeof e && (e = parseInt(e, 10));
                const a = this;
                let n = e;
                n < 0 && (n = 0);
                const { params: l, snapGrid: o, slidesGrid: d, previousIndex: c, activeIndex: p, rtlTranslate: m, wrapperEl: f, enabled: h } = a;
                if ((!h && !i && !r) || a.destroyed || (a.animating && l.preventInteractionOnTransition)) return !1;
                void 0 === t && (t = a.params.speed);
                const v = Math.min(a.params.slidesPerGroupSkip, n);
                let g = v + Math.floor((n - v) / a.params.slidesPerGroup);
                g >= o.length && (g = o.length - 1);
                const w = -o[g];
                if (l.normalizeSlideIndex)
                    for (let e = 0; e < d.length; e += 1) {
                        const t = -Math.floor(100 * w),
                            s = Math.floor(100 * d[e]),
                            i = Math.floor(100 * d[e + 1]);
                        void 0 !== d[e + 1] ? (t >= s && t < i - (i - s) / 2 ? (n = e) : t >= s && t < i && (n = e + 1)) : t >= s && (n = e);
                    }
                if (a.initialized && n !== p) {
                    if (!a.allowSlideNext && (m ? w > a.translate && w > a.minTranslate() : w < a.translate && w < a.minTranslate())) return !1;
                    if (!a.allowSlidePrev && w > a.translate && w > a.maxTranslate() && (p || 0) !== n) return !1;
                }
                let b;
                n !== (c || 0) && s && a.emit("beforeSlideChangeStart"), a.updateProgress(w), (b = n > p ? "next" : n < p ? "prev" : "reset");
                const S = a.virtual && a.params.virtual.enabled;
                if ((!S || !r) && ((m && -w === a.translate) || (!m && w === a.translate)))
                    return a.updateActiveIndex(n), l.autoHeight && a.updateAutoHeight(), a.updateSlidesClasses(), "slide" !== l.effect && a.setTranslate(w), "reset" !== b && (a.transitionStart(s, b), a.transitionEnd(s, b)), !1;
                if (l.cssMode) {
                    const e = a.isHorizontal(),
                        s = m ? w : -w;
                    if (0 === t)
                        S && ((a.wrapperEl.style.scrollSnapType = "none"), (a._immediateVirtual = !0)),
                            S && !a._cssModeVirtualInitialSet && a.params.initialSlide > 0
                                ? ((a._cssModeVirtualInitialSet = !0),
                                  requestAnimationFrame(() => {
                                      f[e ? "scrollLeft" : "scrollTop"] = s;
                                  }))
                                : (f[e ? "scrollLeft" : "scrollTop"] = s),
                            S &&
                                requestAnimationFrame(() => {
                                    (a.wrapperEl.style.scrollSnapType = ""), (a._immediateVirtual = !1);
                                });
                    else {
                        if (!a.support.smoothScroll) return u({ swiper: a, targetPosition: s, side: e ? "left" : "top" }), !0;
                        f.scrollTo({ [e ? "left" : "top"]: s, behavior: "smooth" });
                    }
                    return !0;
                }
                const T = C().isSafari;
                return (
                    S && !r && T && a.isElement && a.virtual.update(!1, !1, n),
                    a.setTransition(t),
                    a.setTranslate(w),
                    a.updateActiveIndex(n),
                    a.updateSlidesClasses(),
                    a.emit("beforeTransitionStart", t, i),
                    a.transitionStart(s, b),
                    0 === t
                        ? a.transitionEnd(s, b)
                        : a.animating ||
                          ((a.animating = !0),
                          a.onSlideToWrapperTransitionEnd ||
                              (a.onSlideToWrapperTransitionEnd = function (e) {
                                  a &&
                                      !a.destroyed &&
                                      e.target === this &&
                                      (a.wrapperEl.removeEventListener("transitionend", a.onSlideToWrapperTransitionEnd), (a.onSlideToWrapperTransitionEnd = null), delete a.onSlideToWrapperTransitionEnd, a.transitionEnd(s, b));
                              }),
                          a.wrapperEl.addEventListener("transitionend", a.onSlideToWrapperTransitionEnd)),
                    !0
                );
            },
            slideToLoop: function (e, t, s, i) {
                void 0 === e && (e = 0), void 0 === s && (s = !0), "string" == typeof e && (e = parseInt(e, 10));
                const r = this;
                if (r.destroyed) return;
                void 0 === t && (t = r.params.speed);
                const a = r.grid && r.params.grid && r.params.grid.rows > 1;
                let n = e;
                if (r.params.loop)
                    if (r.virtual && r.params.virtual.enabled) n += r.virtual.slidesBefore;
                    else {
                        let e;
                        if (a) {
                            const t = n * r.params.grid.rows;
                            e = r.slides.find((e) => 1 * e.getAttribute("data-swiper-slide-index") === t).column;
                        } else e = r.getSlideIndexByData(n);
                        const t = a ? Math.ceil(r.slides.length / r.params.grid.rows) : r.slides.length,
                            { centeredSlides: s } = r.params;
                        let l = r.params.slidesPerView;
                        "auto" === l ? (l = r.slidesPerViewDynamic()) : ((l = Math.ceil(parseFloat(r.params.slidesPerView, 10))), s && l % 2 == 0 && (l += 1));
                        let o = t - e < l;
                        if ((s && (o = o || e < Math.ceil(l / 2)), i && s && "auto" !== r.params.slidesPerView && !a && (o = !1), o)) {
                            const i = s ? (e < r.activeIndex ? "prev" : "next") : e - r.activeIndex - 1 < r.params.slidesPerView ? "next" : "prev";
                            r.loopFix({ direction: i, slideTo: !0, activeSlideIndex: "next" === i ? e + 1 : e - t + 1, slideRealIndex: "next" === i ? r.realIndex : void 0 });
                        }
                        if (a) {
                            const e = n * r.params.grid.rows;
                            n = r.slides.find((t) => 1 * t.getAttribute("data-swiper-slide-index") === e).column;
                        } else n = r.getSlideIndexByData(n);
                    }
                return (
                    requestAnimationFrame(() => {
                        r.slideTo(n, t, s, i);
                    }),
                    r
                );
            },
            slideNext: function (e, t, s) {
                void 0 === t && (t = !0);
                const i = this,
                    { enabled: r, params: a, animating: n } = i;
                if (!r || i.destroyed) return i;
                void 0 === e && (e = i.params.speed);
                let l = a.slidesPerGroup;
                "auto" === a.slidesPerView && 1 === a.slidesPerGroup && a.slidesPerGroupAuto && (l = Math.max(i.slidesPerViewDynamic("current", !0), 1));
                const o = i.activeIndex < a.slidesPerGroupSkip ? 1 : l,
                    d = i.virtual && a.virtual.enabled;
                if (a.loop) {
                    if (n && !d && a.loopPreventsSliding) return !1;
                    if ((i.loopFix({ direction: "next" }), (i._clientLeft = i.wrapperEl.clientLeft), i.activeIndex === i.slides.length - 1 && a.cssMode))
                        return (
                            requestAnimationFrame(() => {
                                i.slideTo(i.activeIndex + o, e, t, s);
                            }),
                            !0
                        );
                }
                return a.rewind && i.isEnd ? i.slideTo(0, e, t, s) : i.slideTo(i.activeIndex + o, e, t, s);
            },
            slidePrev: function (e, t, s) {
                void 0 === t && (t = !0);
                const i = this,
                    { params: r, snapGrid: a, slidesGrid: n, rtlTranslate: l, enabled: o, animating: d } = i;
                if (!o || i.destroyed) return i;
                void 0 === e && (e = i.params.speed);
                const c = i.virtual && r.virtual.enabled;
                if (r.loop) {
                    if (d && !c && r.loopPreventsSliding) return !1;
                    i.loopFix({ direction: "prev" }), (i._clientLeft = i.wrapperEl.clientLeft);
                }
                function p(e) {
                    return e < 0 ? -Math.floor(Math.abs(e)) : Math.floor(e);
                }
                const u = p(l ? i.translate : -i.translate),
                    m = a.map((e) => p(e)),
                    f = r.freeMode && r.freeMode.enabled;
                let h = a[m.indexOf(u) - 1];
                if (void 0 === h && (r.cssMode || f)) {
                    let e;
                    a.forEach((t, s) => {
                        u >= t && (e = s);
                    }),
                        void 0 !== e && (h = f ? a[e] : a[e > 0 ? e - 1 : e]);
                }
                let v = 0;
                if (
                    (void 0 !== h &&
                        ((v = n.indexOf(h)), v < 0 && (v = i.activeIndex - 1), "auto" === r.slidesPerView && 1 === r.slidesPerGroup && r.slidesPerGroupAuto && ((v = v - i.slidesPerViewDynamic("previous", !0) + 1), (v = Math.max(v, 0)))),
                    r.rewind && i.isBeginning)
                ) {
                    const r = i.params.virtual && i.params.virtual.enabled && i.virtual ? i.virtual.slides.length - 1 : i.slides.length - 1;
                    return i.slideTo(r, e, t, s);
                }
                return r.loop && 0 === i.activeIndex && r.cssMode
                    ? (requestAnimationFrame(() => {
                          i.slideTo(v, e, t, s);
                      }),
                      !0)
                    : i.slideTo(v, e, t, s);
            },
            slideReset: function (e, t, s) {
                void 0 === t && (t = !0);
                const i = this;
                if (!i.destroyed) return void 0 === e && (e = i.params.speed), i.slideTo(i.activeIndex, e, t, s);
            },
            slideToClosest: function (e, t, s, i) {
                void 0 === t && (t = !0), void 0 === i && (i = 0.5);
                const r = this;
                if (r.destroyed) return;
                void 0 === e && (e = r.params.speed);
                let a = r.activeIndex;
                const n = Math.min(r.params.slidesPerGroupSkip, a),
                    l = n + Math.floor((a - n) / r.params.slidesPerGroup),
                    o = r.rtlTranslate ? r.translate : -r.translate;
                if (o >= r.snapGrid[l]) {
                    const e = r.snapGrid[l];
                    o - e > (r.snapGrid[l + 1] - e) * i && (a += r.params.slidesPerGroup);
                } else {
                    const e = r.snapGrid[l - 1];
                    o - e <= (r.snapGrid[l] - e) * i && (a -= r.params.slidesPerGroup);
                }
                return (a = Math.max(a, 0)), (a = Math.min(a, r.slidesGrid.length - 1)), r.slideTo(a, e, t, s);
            },
            slideToClickedSlide: function () {
                const e = this;
                if (e.destroyed) return;
                const { params: t, slidesEl: s } = e,
                    i = "auto" === t.slidesPerView ? e.slidesPerViewDynamic() : t.slidesPerView;
                let r,
                    a = e.clickedIndex;
                const n = e.isElement ? "swiper-slide" : `.${t.slideClass}`;
                if (t.loop) {
                    if (e.animating) return;
                    (r = parseInt(e.clickedSlide.getAttribute("data-swiper-slide-index"), 10)),
                        t.centeredSlides
                            ? a < e.loopedSlides - i / 2 || a > e.slides.length - e.loopedSlides + i / 2
                                ? (e.loopFix(),
                                  (a = e.getSlideIndex(m(s, `${n}[data-swiper-slide-index="${r}"]`)[0])),
                                  l(() => {
                                      e.slideTo(a);
                                  }))
                                : e.slideTo(a)
                            : a > e.slides.length - i
                            ? (e.loopFix(),
                              (a = e.getSlideIndex(m(s, `${n}[data-swiper-slide-index="${r}"]`)[0])),
                              l(() => {
                                  e.slideTo(a);
                              }))
                            : e.slideTo(a);
                } else e.slideTo(a);
            },
        },
        _ = {
            loopCreate: function (e, t) {
                const s = this,
                    { params: i, slidesEl: r } = s;
                if (!i.loop || (s.virtual && s.params.virtual.enabled)) return;
                const a = () => {
                        m(r, `.${i.slideClass}, swiper-slide`).forEach((e, t) => {
                            e.setAttribute("data-swiper-slide-index", t);
                        });
                    },
                    n = s.grid && i.grid && i.grid.rows > 1,
                    l = i.slidesPerGroup * (n ? i.grid.rows : 1),
                    o = s.slides.length % l != 0,
                    d = n && s.slides.length % i.grid.rows != 0,
                    c = (e) => {
                        for (let t = 0; t < e; t += 1) {
                            const e = s.isElement ? h("swiper-slide", [i.slideBlankClass]) : h("div", [i.slideClass, i.slideBlankClass]);
                            s.slidesEl.append(e);
                        }
                    };
                o
                    ? (i.loopAddBlankSlides
                          ? (c(l - (s.slides.length % l)), s.recalcSlides(), s.updateSlides())
                          : f("Swiper Loop Warning: The number of slides is not even to slidesPerGroup, loop mode may not function properly. You need to add more slides (or make duplicates, or empty slides)"),
                      a())
                    : d
                    ? (i.loopAddBlankSlides
                          ? (c(i.grid.rows - (s.slides.length % i.grid.rows)), s.recalcSlides(), s.updateSlides())
                          : f("Swiper Loop Warning: The number of slides is not even to grid.rows, loop mode may not function properly. You need to add more slides (or make duplicates, or empty slides)"),
                      a())
                    : a(),
                    s.loopFix({ slideRealIndex: e, direction: i.centeredSlides ? void 0 : "next", initial: t });
            },
            loopFix: function (e) {
                let { slideRealIndex: t, slideTo: s = !0, direction: i, setTranslate: r, activeSlideIndex: a, initial: n, byController: l, byMousewheel: o } = void 0 === e ? {} : e;
                const d = this;
                if (!d.params.loop) return;
                d.emit("beforeLoopFix");
                const { slides: c, allowSlidePrev: p, allowSlideNext: u, slidesEl: m, params: h } = d,
                    { centeredSlides: v, initialSlide: g } = h;
                if (((d.allowSlidePrev = !0), (d.allowSlideNext = !0), d.virtual && h.virtual.enabled))
                    return (
                        s &&
                            (h.centeredSlides || 0 !== d.snapIndex
                                ? h.centeredSlides && d.snapIndex < h.slidesPerView
                                    ? d.slideTo(d.virtual.slides.length + d.snapIndex, 0, !1, !0)
                                    : d.snapIndex === d.snapGrid.length - 1 && d.slideTo(d.virtual.slidesBefore, 0, !1, !0)
                                : d.slideTo(d.virtual.slides.length, 0, !1, !0)),
                        (d.allowSlidePrev = p),
                        (d.allowSlideNext = u),
                        void d.emit("loopFix")
                    );
                let w = h.slidesPerView;
                "auto" === w ? (w = d.slidesPerViewDynamic()) : ((w = Math.ceil(parseFloat(h.slidesPerView, 10))), v && w % 2 == 0 && (w += 1));
                const b = h.slidesPerGroupAuto ? w : h.slidesPerGroup;
                let S = b;
                S % b != 0 && (S += b - (S % b)), (S += h.loopAdditionalSlides), (d.loopedSlides = S);
                const T = d.grid && h.grid && h.grid.rows > 1;
                c.length < w + S || ("cards" === d.params.effect && c.length < w + 2 * S)
                    ? f(
                          "Swiper Loop Warning: The number of slides is not enough for loop mode, it will be disabled or not function properly. You need to add more slides (or make duplicates) or lower the values of slidesPerView and slidesPerGroup parameters"
                      )
                    : T && "row" === h.grid.fill && f("Swiper Loop Warning: Loop mode is not compatible with grid.fill = `row`");
                const y = [],
                    E = [],
                    x = T ? Math.ceil(c.length / h.grid.rows) : c.length,
                    C = n && x - g < w && !v;
                let M = C ? g : d.activeIndex;
                void 0 === a ? (a = d.getSlideIndex(c.find((e) => e.classList.contains(h.slideActiveClass)))) : (M = a);
                const P = "next" === i || !i,
                    L = "prev" === i || !i;
                let k = 0,
                    I = 0;
                const O = (T ? c[a].column : a) + (v && void 0 === r ? -w / 2 + 0.5 : 0);
                if (O < S) {
                    k = Math.max(S - O, b);
                    for (let e = 0; e < S - O; e += 1) {
                        const t = e - Math.floor(e / x) * x;
                        if (T) {
                            const e = x - t - 1;
                            for (let t = c.length - 1; t >= 0; t -= 1) c[t].column === e && y.push(t);
                        } else y.push(x - t - 1);
                    }
                } else if (O + w > x - S) {
                    (I = Math.max(O - (x - 2 * S), b)), C && (I = Math.max(I, w - x + g + 1));
                    for (let e = 0; e < I; e += 1) {
                        const t = e - Math.floor(e / x) * x;
                        T
                            ? c.forEach((e, s) => {
                                  e.column === t && E.push(s);
                              })
                            : E.push(t);
                    }
                }
                if (
                    ((d.__preventObserver__ = !0),
                    requestAnimationFrame(() => {
                        d.__preventObserver__ = !1;
                    }),
                    "cards" === d.params.effect && c.length < w + 2 * S && (E.includes(a) && E.splice(E.indexOf(a), 1), y.includes(a) && y.splice(y.indexOf(a), 1)),
                    L &&
                        y.forEach((e) => {
                            (c[e].swiperLoopMoveDOM = !0), m.prepend(c[e]), (c[e].swiperLoopMoveDOM = !1);
                        }),
                    P &&
                        E.forEach((e) => {
                            (c[e].swiperLoopMoveDOM = !0), m.append(c[e]), (c[e].swiperLoopMoveDOM = !1);
                        }),
                    d.recalcSlides(),
                    "auto" === h.slidesPerView
                        ? d.updateSlides()
                        : T &&
                          ((y.length > 0 && L) || (E.length > 0 && P)) &&
                          d.slides.forEach((e, t) => {
                              d.grid.updateSlide(t, e, d.slides);
                          }),
                    h.watchSlidesProgress && d.updateSlidesOffset(),
                    s)
                )
                    if (y.length > 0 && L) {
                        if (void 0 === t) {
                            const e = d.slidesGrid[M],
                                t = d.slidesGrid[M + k] - e;
                            o
                                ? d.setTranslate(d.translate - t)
                                : (d.slideTo(M + Math.ceil(k), 0, !1, !0), r && ((d.touchEventsData.startTranslate = d.touchEventsData.startTranslate - t), (d.touchEventsData.currentTranslate = d.touchEventsData.currentTranslate - t)));
                        } else if (r) {
                            const e = T ? y.length / h.grid.rows : y.length;
                            d.slideTo(d.activeIndex + e, 0, !1, !0), (d.touchEventsData.currentTranslate = d.translate);
                        }
                    } else if (E.length > 0 && P)
                        if (void 0 === t) {
                            const e = d.slidesGrid[M],
                                t = d.slidesGrid[M - I] - e;
                            o
                                ? d.setTranslate(d.translate - t)
                                : (d.slideTo(M - I, 0, !1, !0), r && ((d.touchEventsData.startTranslate = d.touchEventsData.startTranslate - t), (d.touchEventsData.currentTranslate = d.touchEventsData.currentTranslate - t)));
                        } else {
                            const e = T ? E.length / h.grid.rows : E.length;
                            d.slideTo(d.activeIndex - e, 0, !1, !0);
                        }
                if (((d.allowSlidePrev = p), (d.allowSlideNext = u), d.controller && d.controller.control && !l)) {
                    const e = { slideRealIndex: t, direction: i, setTranslate: r, activeSlideIndex: a, byController: !0 };
                    Array.isArray(d.controller.control)
                        ? d.controller.control.forEach((t) => {
                              !t.destroyed && t.params.loop && t.loopFix({ ...e, slideTo: t.params.slidesPerView === h.slidesPerView && s });
                          })
                        : d.controller.control instanceof d.constructor && d.controller.control.params.loop && d.controller.control.loopFix({ ...e, slideTo: d.controller.control.params.slidesPerView === h.slidesPerView && s });
                }
                d.emit("loopFix");
            },
            loopDestroy: function () {
                const e = this,
                    { params: t, slidesEl: s } = e;
                if (!t.loop || !s || (e.virtual && e.params.virtual.enabled)) return;
                e.recalcSlides();
                const i = [];
                e.slides.forEach((e) => {
                    const t = void 0 === e.swiperSlideIndex ? 1 * e.getAttribute("data-swiper-slide-index") : e.swiperSlideIndex;
                    i[t] = e;
                }),
                    e.slides.forEach((e) => {
                        e.removeAttribute("data-swiper-slide-index");
                    }),
                    i.forEach((e) => {
                        s.append(e);
                    }),
                    e.recalcSlides(),
                    e.slideTo(e.realIndex, 0);
            },
        };
    function G(e, t, s) {
        const i = a(),
            { params: r } = e,
            n = r.edgeSwipeDetection,
            l = r.edgeSwipeThreshold;
        return !n || !(s <= l || s >= i.innerWidth - l) || ("prevent" === n && (t.preventDefault(), !0));
    }
    function V(e) {
        const t = this,
            s = i();
        let r = e;
        r.originalEvent && (r = r.originalEvent);
        const n = t.touchEventsData;
        if ("pointerdown" === r.type) {
            if (null !== n.pointerId && n.pointerId !== r.pointerId) return;
            n.pointerId = r.pointerId;
        } else "touchstart" === r.type && 1 === r.targetTouches.length && (n.touchId = r.targetTouches[0].identifier);
        if ("touchstart" === r.type) return void G(t, r, r.targetTouches[0].pageX);
        const { params: l, touches: d, enabled: c } = t;
        if (!c) return;
        if (!l.simulateTouch && "mouse" === r.pointerType) return;
        if (t.animating && l.preventInteractionOnTransition) return;
        !t.animating && l.cssMode && l.loop && t.loopFix();
        let p = r.target;
        if (
            "wrapper" === l.touchEventsTarget &&
            !(function (e, t) {
                const s = a();
                let i = t.contains(e);
                return (
                    !i &&
                        s.HTMLSlotElement &&
                        t instanceof HTMLSlotElement &&
                        ((i = [...t.assignedElements()].includes(e)),
                        i ||
                            (i = (function (e, t) {
                                const s = [t];
                                for (; s.length > 0; ) {
                                    const t = s.shift();
                                    if (e === t) return !0;
                                    s.push(...t.children, ...(t.shadowRoot ? t.shadowRoot.children : []), ...(t.assignedElements ? t.assignedElements() : []));
                                }
                            })(e, t))),
                    i
                );
            })(p, t.wrapperEl)
        )
            return;
        if ("which" in r && 3 === r.which) return;
        if ("button" in r && r.button > 0) return;
        if (n.isTouched && n.isMoved) return;
        const u = !!l.noSwipingClass && "" !== l.noSwipingClass,
            m = r.composedPath ? r.composedPath() : r.path;
        u && r.target && r.target.shadowRoot && m && (p = m[0]);
        const f = l.noSwipingSelector ? l.noSwipingSelector : `.${l.noSwipingClass}`,
            h = !(!r.target || !r.target.shadowRoot);
        if (
            l.noSwiping &&
            (h
                ? (function (e, t) {
                      return (
                          void 0 === t && (t = this),
                          (function t(s) {
                              if (!s || s === i() || s === a()) return null;
                              s.assignedSlot && (s = s.assignedSlot);
                              const r = s.closest(e);
                              return r || s.getRootNode ? r || t(s.getRootNode().host) : null;
                          })(t)
                      );
                  })(f, p)
                : p.closest(f))
        )
            return void (t.allowClick = !0);
        if (l.swipeHandler && !p.closest(l.swipeHandler)) return;
        (d.currentX = r.pageX), (d.currentY = r.pageY);
        const v = d.currentX,
            g = d.currentY;
        if (!G(t, r, v)) return;
        Object.assign(n, { isTouched: !0, isMoved: !1, allowTouchCallbacks: !0, isScrolling: void 0, startMoving: void 0 }),
            (d.startX = v),
            (d.startY = g),
            (n.touchStartTime = o()),
            (t.allowClick = !0),
            t.updateSize(),
            (t.swipeDirection = void 0),
            l.threshold > 0 && (n.allowThresholdMove = !1);
        let w = !0;
        p.matches(n.focusableElements) && ((w = !1), "SELECT" === p.nodeName && (n.isTouched = !1)),
            s.activeElement && s.activeElement.matches(n.focusableElements) && s.activeElement !== p && ("mouse" === r.pointerType || ("mouse" !== r.pointerType && !p.matches(n.focusableElements))) && s.activeElement.blur();
        const b = w && t.allowTouchMove && l.touchStartPreventDefault;
        (!l.touchStartForcePreventDefault && !b) || p.isContentEditable || r.preventDefault(), l.freeMode && l.freeMode.enabled && t.freeMode && t.animating && !l.cssMode && t.freeMode.onTouchStart(), t.emit("touchStart", r);
    }
    function B(e) {
        const t = i(),
            s = this,
            r = s.touchEventsData,
            { params: a, touches: n, rtlTranslate: l, enabled: d } = s;
        if (!d) return;
        if (!a.simulateTouch && "mouse" === e.pointerType) return;
        let c,
            p = e;
        if ((p.originalEvent && (p = p.originalEvent), "pointermove" === p.type)) {
            if (null !== r.touchId) return;
            if (p.pointerId !== r.pointerId) return;
        }
        if ("touchmove" === p.type) {
            if (((c = [...p.changedTouches].find((e) => e.identifier === r.touchId)), !c || c.identifier !== r.touchId)) return;
        } else c = p;
        if (!r.isTouched) return void (r.startMoving && r.isScrolling && s.emit("touchMoveOpposite", p));
        const u = c.pageX,
            m = c.pageY;
        if (p.preventedByNestedSwiper) return (n.startX = u), void (n.startY = m);
        if (!s.allowTouchMove) return p.target.matches(r.focusableElements) || (s.allowClick = !1), void (r.isTouched && (Object.assign(n, { startX: u, startY: m, currentX: u, currentY: m }), (r.touchStartTime = o())));
        if (a.touchReleaseOnEdges && !a.loop)
            if (s.isVertical()) {
                if ((m < n.startY && s.translate <= s.maxTranslate()) || (m > n.startY && s.translate >= s.minTranslate())) return (r.isTouched = !1), void (r.isMoved = !1);
            } else {
                if (l && ((u > n.startX && -s.translate <= s.maxTranslate()) || (u < n.startX && -s.translate >= s.minTranslate()))) return;
                if (!l && ((u < n.startX && s.translate <= s.maxTranslate()) || (u > n.startX && s.translate >= s.minTranslate()))) return;
            }
        if (
            (t.activeElement && t.activeElement.matches(r.focusableElements) && t.activeElement !== p.target && "mouse" !== p.pointerType && t.activeElement.blur(),
            t.activeElement && p.target === t.activeElement && p.target.matches(r.focusableElements))
        )
            return (r.isMoved = !0), void (s.allowClick = !1);
        r.allowTouchCallbacks && s.emit("touchMove", p), (n.previousX = n.currentX), (n.previousY = n.currentY), (n.currentX = u), (n.currentY = m);
        const f = n.currentX - n.startX,
            h = n.currentY - n.startY;
        if (s.params.threshold && Math.sqrt(f ** 2 + h ** 2) < s.params.threshold) return;
        if (void 0 === r.isScrolling) {
            let e;
            (s.isHorizontal() && n.currentY === n.startY) || (s.isVertical() && n.currentX === n.startX)
                ? (r.isScrolling = !1)
                : f * f + h * h >= 25 && ((e = (180 * Math.atan2(Math.abs(h), Math.abs(f))) / Math.PI), (r.isScrolling = s.isHorizontal() ? e > a.touchAngle : 90 - e > a.touchAngle));
        }
        if (
            (r.isScrolling && s.emit("touchMoveOpposite", p),
            void 0 === r.startMoving && ((n.currentX === n.startX && n.currentY === n.startY) || (r.startMoving = !0)),
            r.isScrolling || ("touchmove" === p.type && r.preventTouchMoveFromPointerMove))
        )
            return void (r.isTouched = !1);
        if (!r.startMoving) return;
        (s.allowClick = !1), !a.cssMode && p.cancelable && p.preventDefault(), a.touchMoveStopPropagation && !a.nested && p.stopPropagation();
        let v = s.isHorizontal() ? f : h,
            g = s.isHorizontal() ? n.currentX - n.previousX : n.currentY - n.previousY;
        a.oneWayMovement && ((v = Math.abs(v) * (l ? 1 : -1)), (g = Math.abs(g) * (l ? 1 : -1))), (n.diff = v), (v *= a.touchRatio), l && ((v = -v), (g = -g));
        const w = s.touchesDirection;
        (s.swipeDirection = v > 0 ? "prev" : "next"), (s.touchesDirection = g > 0 ? "prev" : "next");
        const b = s.params.loop && !a.cssMode,
            S = ("next" === s.touchesDirection && s.allowSlideNext) || ("prev" === s.touchesDirection && s.allowSlidePrev);
        if (!r.isMoved) {
            if ((b && S && s.loopFix({ direction: s.swipeDirection }), (r.startTranslate = s.getTranslate()), s.setTransition(0), s.animating)) {
                const e = new window.CustomEvent("transitionend", { bubbles: !0, cancelable: !0, detail: { bySwiperTouchMove: !0 } });
                s.wrapperEl.dispatchEvent(e);
            }
            (r.allowMomentumBounce = !1), !a.grabCursor || (!0 !== s.allowSlideNext && !0 !== s.allowSlidePrev) || s.setGrabCursor(!0), s.emit("sliderFirstMove", p);
        }
        if ((new Date().getTime(), !1 !== a._loopSwapReset && r.isMoved && r.allowThresholdMove && w !== s.touchesDirection && b && S && Math.abs(v) >= 1))
            return Object.assign(n, { startX: u, startY: m, currentX: u, currentY: m, startTranslate: r.currentTranslate }), (r.loopSwapReset = !0), void (r.startTranslate = r.currentTranslate);
        s.emit("sliderMove", p), (r.isMoved = !0), (r.currentTranslate = v + r.startTranslate);
        let T = !0,
            y = a.resistanceRatio;
        if (
            (a.touchReleaseOnEdges && (y = 0),
            v > 0
                ? (b &&
                      S &&
                      r.allowThresholdMove &&
                      r.currentTranslate >
                          (a.centeredSlides
                              ? s.minTranslate() -
                                s.slidesSizesGrid[s.activeIndex + 1] -
                                ("auto" !== a.slidesPerView && s.slides.length - a.slidesPerView >= 2 ? s.slidesSizesGrid[s.activeIndex + 1] + s.params.spaceBetween : 0) -
                                s.params.spaceBetween
                              : s.minTranslate()) &&
                      s.loopFix({ direction: "prev", setTranslate: !0, activeSlideIndex: 0 }),
                  r.currentTranslate > s.minTranslate() && ((T = !1), a.resistance && (r.currentTranslate = s.minTranslate() - 1 + (-s.minTranslate() + r.startTranslate + v) ** y)))
                : v < 0 &&
                  (b &&
                      S &&
                      r.allowThresholdMove &&
                      r.currentTranslate <
                          (a.centeredSlides
                              ? s.maxTranslate() +
                                s.slidesSizesGrid[s.slidesSizesGrid.length - 1] +
                                s.params.spaceBetween +
                                ("auto" !== a.slidesPerView && s.slides.length - a.slidesPerView >= 2 ? s.slidesSizesGrid[s.slidesSizesGrid.length - 1] + s.params.spaceBetween : 0)
                              : s.maxTranslate()) &&
                      s.loopFix({ direction: "next", setTranslate: !0, activeSlideIndex: s.slides.length - ("auto" === a.slidesPerView ? s.slidesPerViewDynamic() : Math.ceil(parseFloat(a.slidesPerView, 10))) }),
                  r.currentTranslate < s.maxTranslate() && ((T = !1), a.resistance && (r.currentTranslate = s.maxTranslate() + 1 - (s.maxTranslate() - r.startTranslate - v) ** y))),
            T && (p.preventedByNestedSwiper = !0),
            !s.allowSlideNext && "next" === s.swipeDirection && r.currentTranslate < r.startTranslate && (r.currentTranslate = r.startTranslate),
            !s.allowSlidePrev && "prev" === s.swipeDirection && r.currentTranslate > r.startTranslate && (r.currentTranslate = r.startTranslate),
            s.allowSlidePrev || s.allowSlideNext || (r.currentTranslate = r.startTranslate),
            a.threshold > 0)
        ) {
            if (!(Math.abs(v) > a.threshold || r.allowThresholdMove)) return void (r.currentTranslate = r.startTranslate);
            if (!r.allowThresholdMove)
                return (r.allowThresholdMove = !0), (n.startX = n.currentX), (n.startY = n.currentY), (r.currentTranslate = r.startTranslate), void (n.diff = s.isHorizontal() ? n.currentX - n.startX : n.currentY - n.startY);
        }
        a.followFinger &&
            !a.cssMode &&
            (((a.freeMode && a.freeMode.enabled && s.freeMode) || a.watchSlidesProgress) && (s.updateActiveIndex(), s.updateSlidesClasses()),
            a.freeMode && a.freeMode.enabled && s.freeMode && s.freeMode.onTouchMove(),
            s.updateProgress(r.currentTranslate),
            s.setTranslate(r.currentTranslate));
    }
    function N(e) {
        const t = this,
            s = t.touchEventsData;
        let i,
            r = e;
        if ((r.originalEvent && (r = r.originalEvent), "touchend" === r.type || "touchcancel" === r.type)) {
            if (((i = [...r.changedTouches].find((e) => e.identifier === s.touchId)), !i || i.identifier !== s.touchId)) return;
        } else {
            if (null !== s.touchId) return;
            if (r.pointerId !== s.pointerId) return;
            i = r;
        }
        if (["pointercancel", "pointerout", "pointerleave", "contextmenu"].includes(r.type) && (!["pointercancel", "contextmenu"].includes(r.type) || (!t.browser.isSafari && !t.browser.isWebView))) return;
        (s.pointerId = null), (s.touchId = null);
        const { params: a, touches: n, rtlTranslate: d, slidesGrid: c, enabled: p } = t;
        if (!p) return;
        if (!a.simulateTouch && "mouse" === r.pointerType) return;
        if ((s.allowTouchCallbacks && t.emit("touchEnd", r), (s.allowTouchCallbacks = !1), !s.isTouched)) return s.isMoved && a.grabCursor && t.setGrabCursor(!1), (s.isMoved = !1), void (s.startMoving = !1);
        a.grabCursor && s.isMoved && s.isTouched && (!0 === t.allowSlideNext || !0 === t.allowSlidePrev) && t.setGrabCursor(!1);
        const u = o(),
            m = u - s.touchStartTime;
        if (t.allowClick) {
            const e = r.path || (r.composedPath && r.composedPath());
            t.updateClickedSlide((e && e[0]) || r.target, e), t.emit("tap click", r), m < 300 && u - s.lastClickTime < 300 && t.emit("doubleTap doubleClick", r);
        }
        if (
            ((s.lastClickTime = o()),
            l(() => {
                t.destroyed || (t.allowClick = !0);
            }),
            !s.isTouched || !s.isMoved || !t.swipeDirection || (0 === n.diff && !s.loopSwapReset) || (s.currentTranslate === s.startTranslate && !s.loopSwapReset))
        )
            return (s.isTouched = !1), (s.isMoved = !1), void (s.startMoving = !1);
        let f;
        if (((s.isTouched = !1), (s.isMoved = !1), (s.startMoving = !1), (f = a.followFinger ? (d ? t.translate : -t.translate) : -s.currentTranslate), a.cssMode)) return;
        if (a.freeMode && a.freeMode.enabled) return void t.freeMode.onTouchEnd({ currentPos: f });
        const h = f >= -t.maxTranslate() && !t.params.loop;
        let v = 0,
            g = t.slidesSizesGrid[0];
        for (let e = 0; e < c.length; e += e < a.slidesPerGroupSkip ? 1 : a.slidesPerGroup) {
            const t = e < a.slidesPerGroupSkip - 1 ? 1 : a.slidesPerGroup;
            void 0 !== c[e + t] ? (h || (f >= c[e] && f < c[e + t])) && ((v = e), (g = c[e + t] - c[e])) : (h || f >= c[e]) && ((v = e), (g = c[c.length - 1] - c[c.length - 2]));
        }
        let w = null,
            b = null;
        a.rewind && (t.isBeginning ? (b = a.virtual && a.virtual.enabled && t.virtual ? t.virtual.slides.length - 1 : t.slides.length - 1) : t.isEnd && (w = 0));
        const S = (f - c[v]) / g,
            T = v < a.slidesPerGroupSkip - 1 ? 1 : a.slidesPerGroup;
        if (m > a.longSwipesMs) {
            if (!a.longSwipes) return void t.slideTo(t.activeIndex);
            "next" === t.swipeDirection && (S >= a.longSwipesRatio ? t.slideTo(a.rewind && t.isEnd ? w : v + T) : t.slideTo(v)),
                "prev" === t.swipeDirection && (S > 1 - a.longSwipesRatio ? t.slideTo(v + T) : null !== b && S < 0 && Math.abs(S) > a.longSwipesRatio ? t.slideTo(b) : t.slideTo(v));
        } else {
            if (!a.shortSwipes) return void t.slideTo(t.activeIndex);
            !t.navigation || (r.target !== t.navigation.nextEl && r.target !== t.navigation.prevEl)
                ? ("next" === t.swipeDirection && t.slideTo(null !== w ? w : v + T), "prev" === t.swipeDirection && t.slideTo(null !== b ? b : v))
                : r.target === t.navigation.nextEl
                ? t.slideTo(v + T)
                : t.slideTo(v);
        }
    }
    function F() {
        const e = this,
            { params: t, el: s } = e;
        if (s && 0 === s.offsetWidth) return;
        t.breakpoints && e.setBreakpoint();
        const { allowSlideNext: i, allowSlidePrev: r, snapGrid: a } = e,
            n = e.virtual && e.params.virtual.enabled;
        (e.allowSlideNext = !0), (e.allowSlidePrev = !0), e.updateSize(), e.updateSlides(), e.updateSlidesClasses();
        const l = n && t.loop;
        !("auto" === t.slidesPerView || t.slidesPerView > 1) || !e.isEnd || e.isBeginning || e.params.centeredSlides || l
            ? e.params.loop && !n
                ? e.slideToLoop(e.realIndex, 0, !1, !0)
                : e.slideTo(e.activeIndex, 0, !1, !0)
            : e.slideTo(e.slides.length - 1, 0, !1, !0),
            e.autoplay &&
                e.autoplay.running &&
                e.autoplay.paused &&
                (clearTimeout(e.autoplay.resizeTimeout),
                (e.autoplay.resizeTimeout = setTimeout(() => {
                    e.autoplay && e.autoplay.running && e.autoplay.paused && e.autoplay.resume();
                }, 500))),
            (e.allowSlidePrev = r),
            (e.allowSlideNext = i),
            e.params.watchOverflow && a !== e.snapGrid && e.checkOverflow();
    }
    function H(e) {
        const t = this;
        t.enabled && (t.allowClick || (t.params.preventClicks && e.preventDefault(), t.params.preventClicksPropagation && t.animating && (e.stopPropagation(), e.stopImmediatePropagation())));
    }
    function $() {
        const e = this,
            { wrapperEl: t, rtlTranslate: s, enabled: i } = e;
        if (!i) return;
        let r;
        (e.previousTranslate = e.translate), e.isHorizontal() ? (e.translate = -t.scrollLeft) : (e.translate = -t.scrollTop), 0 === e.translate && (e.translate = 0), e.updateActiveIndex(), e.updateSlidesClasses();
        const a = e.maxTranslate() - e.minTranslate();
        (r = 0 === a ? 0 : (e.translate - e.minTranslate()) / a), r !== e.progress && e.updateProgress(s ? -e.translate : e.translate), e.emit("setTranslate", e.translate, !1);
    }
    function R(e) {
        const t = this;
        k(t, e.target), t.params.cssMode || ("auto" !== t.params.slidesPerView && !t.params.autoHeight) || t.update();
    }
    function j() {
        const e = this;
        e.documentTouchHandlerProceeded || ((e.documentTouchHandlerProceeded = !0), e.params.touchReleaseOnEdges && (e.el.style.touchAction = "auto"));
    }
    const q = (e, t) => {
            const s = i(),
                { params: r, el: a, wrapperEl: n, device: l } = e,
                o = !!r.nested,
                d = "on" === t ? "addEventListener" : "removeEventListener",
                c = t;
            a &&
                "string" != typeof a &&
                (s[d]("touchstart", e.onDocumentTouchStart, { passive: !1, capture: o }),
                a[d]("touchstart", e.onTouchStart, { passive: !1 }),
                a[d]("pointerdown", e.onTouchStart, { passive: !1 }),
                s[d]("touchmove", e.onTouchMove, { passive: !1, capture: o }),
                s[d]("pointermove", e.onTouchMove, { passive: !1, capture: o }),
                s[d]("touchend", e.onTouchEnd, { passive: !0 }),
                s[d]("pointerup", e.onTouchEnd, { passive: !0 }),
                s[d]("pointercancel", e.onTouchEnd, { passive: !0 }),
                s[d]("touchcancel", e.onTouchEnd, { passive: !0 }),
                s[d]("pointerout", e.onTouchEnd, { passive: !0 }),
                s[d]("pointerleave", e.onTouchEnd, { passive: !0 }),
                s[d]("contextmenu", e.onTouchEnd, { passive: !0 }),
                (r.preventClicks || r.preventClicksPropagation) && a[d]("click", e.onClick, !0),
                r.cssMode && n[d]("scroll", e.onScroll),
                r.updateOnWindowResize ? e[c](l.ios || l.android ? "resize orientationchange observerUpdate" : "resize observerUpdate", F, !0) : e[c]("observerUpdate", F, !0),
                a[d]("load", e.onLoad, { capture: !0 }));
        },
        W = (e, t) => e.grid && t.grid && t.grid.rows > 1;
    var X = {
        init: !0,
        direction: "horizontal",
        oneWayMovement: !1,
        swiperElementNodeName: "SWIPER-CONTAINER",
        touchEventsTarget: "wrapper",
        initialSlide: 0,
        speed: 300,
        cssMode: !1,
        updateOnWindowResize: !0,
        resizeObserver: !0,
        nested: !1,
        createElements: !1,
        eventsPrefix: "swiper",
        enabled: !0,
        focusableElements: "input, select, option, textarea, button, video, label",
        width: null,
        height: null,
        preventInteractionOnTransition: !1,
        userAgent: null,
        url: null,
        edgeSwipeDetection: !1,
        edgeSwipeThreshold: 20,
        autoHeight: !1,
        setWrapperSize: !1,
        virtualTranslate: !1,
        effect: "slide",
        breakpoints: void 0,
        breakpointsBase: "window",
        spaceBetween: 0,
        slidesPerView: 1,
        slidesPerGroup: 1,
        slidesPerGroupSkip: 0,
        slidesPerGroupAuto: !1,
        centeredSlides: !1,
        centeredSlidesBounds: !1,
        slidesOffsetBefore: 0,
        slidesOffsetAfter: 0,
        normalizeSlideIndex: !0,
        centerInsufficientSlides: !1,
        watchOverflow: !0,
        roundLengths: !1,
        touchRatio: 1,
        touchAngle: 45,
        simulateTouch: !0,
        shortSwipes: !0,
        longSwipes: !0,
        longSwipesRatio: 0.5,
        longSwipesMs: 300,
        followFinger: !0,
        allowTouchMove: !0,
        threshold: 5,
        touchMoveStopPropagation: !1,
        touchStartPreventDefault: !0,
        touchStartForcePreventDefault: !1,
        touchReleaseOnEdges: !1,
        uniqueNavElements: !0,
        resistance: !0,
        resistanceRatio: 0.85,
        watchSlidesProgress: !1,
        grabCursor: !1,
        preventClicks: !0,
        preventClicksPropagation: !0,
        slideToClickedSlide: !1,
        loop: !1,
        loopAddBlankSlides: !0,
        loopAdditionalSlides: 0,
        loopPreventsSliding: !0,
        rewind: !1,
        allowSlidePrev: !0,
        allowSlideNext: !0,
        swipeHandler: null,
        noSwiping: !0,
        noSwipingClass: "swiper-no-swiping",
        noSwipingSelector: null,
        passiveListeners: !0,
        maxBackfaceHiddenSlides: 10,
        containerModifierClass: "swiper-",
        slideClass: "swiper-slide",
        slideBlankClass: "swiper-slide-blank",
        slideActiveClass: "swiper-slide-active",
        slideVisibleClass: "swiper-slide-visible",
        slideFullyVisibleClass: "swiper-slide-fully-visible",
        slideNextClass: "swiper-slide-next",
        slidePrevClass: "swiper-slide-prev",
        wrapperClass: "swiper-wrapper",
        lazyPreloaderClass: "swiper-lazy-preloader",
        lazyPreloadPrevNext: 0,
        runCallbacksOnInit: !0,
        _emitClasses: !1,
    };
    function Y(e, t) {
        return function (s) {
            void 0 === s && (s = {});
            const i = Object.keys(s)[0],
                r = s[i];
            "object" == typeof r && null !== r
                ? (!0 === e[i] && (e[i] = { enabled: !0 }),
                    "navigation" === i && e[i] && e[i].enabled && !e[i].prevEl && !e[i].nextEl && (e[i].auto = !0),
                    ["pagination", "scrollbar"].indexOf(i) >= 0 && e[i] && e[i].enabled && !e[i].el && (e[i].auto = !0),
                    i in e && "enabled" in r ? ("object" != typeof e[i] || "enabled" in e[i] || (e[i].enabled = !0), e[i] || (e[i] = { enabled: !1 }), c(t, s)) : c(t, s))
                : c(t, s);
        };
    }
    const U = {
            eventsEmitter: M,
            update: z,
            translate: {
                getTranslate: function (e) {
                    void 0 === e && (e = this.isHorizontal() ? "x" : "y");
                    const { params: t, rtlTranslate: s, translate: i, wrapperEl: r } = this;
                    if (t.virtualTranslate) return s ? -i : i;
                    if (t.cssMode) return i;
                    let n = (function (e, t) {
                        void 0 === t && (t = "x");
                        const s = a();
                        let i, r, n;
                        const l = (function (e) {
                            const t = a();
                            let s;
                            return t.getComputedStyle && (s = t.getComputedStyle(e, null)), !s && e.currentStyle && (s = e.currentStyle), s || (s = e.style), s;
                        })(e);
                        return (
                            s.WebKitCSSMatrix
                                ? ((r = l.transform || l.webkitTransform),
                                    r.split(",").length > 6 &&
                                        (r = r
                                            .split(", ")
                                            .map((e) => e.replace(",", "."))
                                            .join(", ")),
                                    (n = new s.WebKitCSSMatrix("none" === r ? "" : r)))
                                : ((n = l.MozTransform || l.OTransform || l.MsTransform || l.msTransform || l.transform || l.getPropertyValue("transform").replace("translate(", "matrix(1, 0, 0, 1,")), (i = n.toString().split(","))),
                            "x" === t && (r = s.WebKitCSSMatrix ? n.m41 : 16 === i.length ? parseFloat(i[12]) : parseFloat(i[4])),
                            "y" === t && (r = s.WebKitCSSMatrix ? n.m42 : 16 === i.length ? parseFloat(i[13]) : parseFloat(i[5])),
                            r || 0
                        );
                    })(r, e);
                    return (n += this.cssOverflowAdjustment()), s && (n = -n), n || 0;
                },
                setTranslate: function (e, t) {
                    const s = this,
                        { rtlTranslate: i, params: r, wrapperEl: a, progress: n } = s;
                    let l,
                        o = 0,
                        d = 0;
                    s.isHorizontal() ? (o = i ? -e : e) : (d = e),
                        r.roundLengths && ((o = Math.floor(o)), (d = Math.floor(d))),
                        (s.previousTranslate = s.translate),
                        (s.translate = s.isHorizontal() ? o : d),
                        r.cssMode
                            ? (a[s.isHorizontal() ? "scrollLeft" : "scrollTop"] = s.isHorizontal() ? -o : -d)
                            : r.virtualTranslate || (s.isHorizontal() ? (o -= s.cssOverflowAdjustment()) : (d -= s.cssOverflowAdjustment()), (a.style.transform = `translate3d(${o}px, ${d}px, 0px)`));
                    const c = s.maxTranslate() - s.minTranslate();
                    (l = 0 === c ? 0 : (e - s.minTranslate()) / c), l !== n && s.updateProgress(e), s.emit("setTranslate", s.translate, t);
                },
                minTranslate: function () {
                    return -this.snapGrid[0];
                },
                maxTranslate: function () {
                    return -this.snapGrid[this.snapGrid.length - 1];
                },
                translateTo: function (e, t, s, i, r) {
                    void 0 === e && (e = 0), void 0 === t && (t = this.params.speed), void 0 === s && (s = !0), void 0 === i && (i = !0);
                    const a = this,
                        { params: n, wrapperEl: l } = a;
                    if (a.animating && n.preventInteractionOnTransition) return !1;
                    const o = a.minTranslate(),
                        d = a.maxTranslate();
                    let c;
                    if (((c = i && e > o ? o : i && e < d ? d : e), a.updateProgress(c), n.cssMode)) {
                        const e = a.isHorizontal();
                        if (0 === t) l[e ? "scrollLeft" : "scrollTop"] = -c;
                        else {
                            if (!a.support.smoothScroll) return u({ swiper: a, targetPosition: -c, side: e ? "left" : "top" }), !0;
                            l.scrollTo({ [e ? "left" : "top"]: -c, behavior: "smooth" });
                        }
                        return !0;
                    }
                    return (
                        0 === t
                            ? (a.setTransition(0), a.setTranslate(c), s && (a.emit("beforeTransitionStart", t, r), a.emit("transitionEnd")))
                            : (a.setTransition(t),
                                a.setTranslate(c),
                                s && (a.emit("beforeTransitionStart", t, r), a.emit("transitionStart")),
                                a.animating ||
                                    ((a.animating = !0),
                                    a.onTranslateToWrapperTransitionEnd ||
                                        (a.onTranslateToWrapperTransitionEnd = function (e) {
                                            a &&
                                                !a.destroyed &&
                                                e.target === this &&
                                                (a.wrapperEl.removeEventListener("transitionend", a.onTranslateToWrapperTransitionEnd),
                                                (a.onTranslateToWrapperTransitionEnd = null),
                                                delete a.onTranslateToWrapperTransitionEnd,
                                                (a.animating = !1),
                                                s && a.emit("transitionEnd"));
                                        }),
                                    a.wrapperEl.addEventListener("transitionend", a.onTranslateToWrapperTransitionEnd))),
                        !0
                    );
                },
            },
            transition: {
                setTransition: function (e, t) {
                    const s = this;
                    s.params.cssMode || ((s.wrapperEl.style.transitionDuration = `${e}ms`), (s.wrapperEl.style.transitionDelay = 0 === e ? "0ms" : "")), s.emit("setTransition", e, t);
                },
                transitionStart: function (e, t) {
                    void 0 === e && (e = !0);
                    const s = this,
                        { params: i } = s;
                    i.cssMode || (i.autoHeight && s.updateAutoHeight(), A({ swiper: s, runCallbacks: e, direction: t, step: "Start" }));
                },
                transitionEnd: function (e, t) {
                    void 0 === e && (e = !0);
                    const s = this,
                        { params: i } = s;
                    (s.animating = !1), i.cssMode || (s.setTransition(0), A({ swiper: s, runCallbacks: e, direction: t, step: "End" }));
                },
            },
            slide: D,
            loop: _,
            grabCursor: {
                setGrabCursor: function (e) {
                    const t = this;
                    if (!t.params.simulateTouch || (t.params.watchOverflow && t.isLocked) || t.params.cssMode) return;
                    const s = "container" === t.params.touchEventsTarget ? t.el : t.wrapperEl;
                    t.isElement && (t.__preventObserver__ = !0),
                        (s.style.cursor = "move"),
                        (s.style.cursor = e ? "grabbing" : "grab"),
                        t.isElement &&
                            requestAnimationFrame(() => {
                                t.__preventObserver__ = !1;
                            });
                },
                unsetGrabCursor: function () {
                    const e = this;
                    (e.params.watchOverflow && e.isLocked) ||
                        e.params.cssMode ||
                        (e.isElement && (e.__preventObserver__ = !0),
                        (e["container" === e.params.touchEventsTarget ? "el" : "wrapperEl"].style.cursor = ""),
                        e.isElement &&
                            requestAnimationFrame(() => {
                                e.__preventObserver__ = !1;
                            }));
                },
            },
            events: {
                attachEvents: function () {
                    const e = this,
                        { params: t } = e;
                    (e.onTouchStart = V.bind(e)),
                        (e.onTouchMove = B.bind(e)),
                        (e.onTouchEnd = N.bind(e)),
                        (e.onDocumentTouchStart = j.bind(e)),
                        t.cssMode && (e.onScroll = $.bind(e)),
                        (e.onClick = H.bind(e)),
                        (e.onLoad = R.bind(e)),
                        q(e, "on");
                },
                detachEvents: function () {
                    q(this, "off");
                },
            },
            breakpoints: {
                setBreakpoint: function () {
                    const e = this,
                        { realIndex: t, initialized: s, params: r, el: a } = e,
                        n = r.breakpoints;
                    if (!n || (n && 0 === Object.keys(n).length)) return;
                    const l = i(),
                        o = "window" !== r.breakpointsBase && r.breakpointsBase ? "container" : r.breakpointsBase,
                        d = ["window", "container"].includes(r.breakpointsBase) || !r.breakpointsBase ? e.el : l.querySelector(r.breakpointsBase),
                        p = e.getBreakpoint(n, o, d);
                    if (!p || e.currentBreakpoint === p) return;
                    const u = (p in n ? n[p] : void 0) || e.originalParams,
                        m = W(e, r),
                        f = W(e, u),
                        h = e.params.grabCursor,
                        v = u.grabCursor,
                        g = r.enabled;
                    m && !f
                        ? (a.classList.remove(`${r.containerModifierClass}grid`, `${r.containerModifierClass}grid-column`), e.emitContainerClasses())
                        : !m &&
                            f &&
                            (a.classList.add(`${r.containerModifierClass}grid`),
                            ((u.grid.fill && "column" === u.grid.fill) || (!u.grid.fill && "column" === r.grid.fill)) && a.classList.add(`${r.containerModifierClass}grid-column`),
                            e.emitContainerClasses()),
                        h && !v ? e.unsetGrabCursor() : !h && v && e.setGrabCursor(),
                        ["navigation", "pagination", "scrollbar"].forEach((t) => {
                            if (void 0 === u[t]) return;
                            const s = r[t] && r[t].enabled,
                                i = u[t] && u[t].enabled;
                            s && !i && e[t].disable(), !s && i && e[t].enable();
                        });
                    const w = u.direction && u.direction !== r.direction,
                        b = r.loop && (u.slidesPerView !== r.slidesPerView || w),
                        S = r.loop;
                    w && s && e.changeDirection(), c(e.params, u);
                    const T = e.params.enabled,
                        y = e.params.loop;
                    Object.assign(e, { allowTouchMove: e.params.allowTouchMove, allowSlideNext: e.params.allowSlideNext, allowSlidePrev: e.params.allowSlidePrev }),
                        g && !T ? e.disable() : !g && T && e.enable(),
                        (e.currentBreakpoint = p),
                        e.emit("_beforeBreakpoint", u),
                        s && (b ? (e.loopDestroy(), e.loopCreate(t), e.updateSlides()) : !S && y ? (e.loopCreate(t), e.updateSlides()) : S && !y && e.loopDestroy()),
                        e.emit("breakpoint", u);
                },
                getBreakpoint: function (e, t, s) {
                    if ((void 0 === t && (t = "window"), !e || ("container" === t && !s))) return;
                    let i = !1;
                    const r = a(),
                        n = "window" === t ? r.innerHeight : s.clientHeight,
                        l = Object.keys(e).map((e) => {
                            if ("string" == typeof e && 0 === e.indexOf("@")) {
                                const t = parseFloat(e.substr(1));
                                return { value: n * t, point: e };
                            }
                            return { value: e, point: e };
                        });
                    l.sort((e, t) => parseInt(e.value, 10) - parseInt(t.value, 10));
                    for (let e = 0; e < l.length; e += 1) {
                        const { point: a, value: n } = l[e];
                        "window" === t ? r.matchMedia(`(min-width: ${n}px)`).matches && (i = a) : n <= s.clientWidth && (i = a);
                    }
                    return i || "max";
                },
            },
            checkOverflow: {
                checkOverflow: function () {
                    const e = this,
                        { isLocked: t, params: s } = e,
                        { slidesOffsetBefore: i } = s;
                    if (i) {
                        const t = e.slides.length - 1,
                            s = e.slidesGrid[t] + e.slidesSizesGrid[t] + 2 * i;
                        e.isLocked = e.size > s;
                    } else e.isLocked = 1 === e.snapGrid.length;
                    !0 === s.allowSlideNext && (e.allowSlideNext = !e.isLocked),
                        !0 === s.allowSlidePrev && (e.allowSlidePrev = !e.isLocked),
                        t && t !== e.isLocked && (e.isEnd = !1),
                        t !== e.isLocked && e.emit(e.isLocked ? "lock" : "unlock");
                },
            },
            classes: {
                addClasses: function () {
                    const e = this,
                        { classNames: t, params: s, rtl: i, el: r, device: a } = e,
                        n = (function (e, t) {
                            const s = [];
                            return (
                                e.forEach((e) => {
                                    "object" == typeof e
                                        ? Object.keys(e).forEach((i) => {
                                              e[i] && s.push(t + i);
                                          })
                                        : "string" == typeof e && s.push(t + e);
                                }),
                                s
                            );
                        })(
                            [
                                "initialized",
                                s.direction,
                                { "free-mode": e.params.freeMode && s.freeMode.enabled },
                                { autoheight: s.autoHeight },
                                { rtl: i },
                                { grid: s.grid && s.grid.rows > 1 },
                                { "grid-column": s.grid && s.grid.rows > 1 && "column" === s.grid.fill },
                                { android: a.android },
                                { ios: a.ios },
                                { "css-mode": s.cssMode },
                                { centered: s.cssMode && s.centeredSlides },
                                { "watch-progress": s.watchSlidesProgress },
                            ],
                            s.containerModifierClass
                        );
                    t.push(...n), r.classList.add(...t), e.emitContainerClasses();
                },
                removeClasses: function () {
                    const { el: e, classNames: t } = this;
                    e && "string" != typeof e && (e.classList.remove(...t), this.emitContainerClasses());
                },
            },
        },
        K = {};
    class J { // <-- Definition of J (Swiper class)
        constructor() {
            let e, t;
            for (var s = arguments.length, r = new Array(s), a = 0; a < s; a++) r[a] = arguments[a];
            1 === r.length && r[0].constructor && "Object" === Object.prototype.toString.call(r[0]).slice(8, -1) ? (t = r[0]) : ([e, t] = r), t || (t = {}), (t = c({}, t)), e && !t.el && (t.el = e);
            const n = i();
            if (t.el && "string" == typeof t.el && n.querySelectorAll(t.el).length > 1) {
                const e = [];
                return (
                    n.querySelectorAll(t.el).forEach((s) => {
                        const i = c({}, t, { el: s });
                        e.push(new J(i));
                    }),
                    e
                );
            }
            const l = this;
            (l.__swiper__ = !0),
                (l.support = E()),
                (l.device = x({ userAgent: t.userAgent })),
                (l.browser = C()),
                (l.eventsListeners = {}),
                (l.eventsAnyListeners = []),
                (l.modules = [...l.__modules__]),
                t.modules && Array.isArray(t.modules) && l.modules.push(...t.modules);
            const o = {};
            l.modules.forEach((e) => {
                e({ params: t, swiper: l, extendParams: Y(t, o), on: l.on.bind(l), once: l.once.bind(l), off: l.off.bind(l), emit: l.emit.bind(l) });
            });
            const d = c({}, X, o);
            return (
                (l.params = c({}, d, K, t)),
                (l.originalParams = c({}, l.params)),
                (l.passedParams = c({}, t)),
                l.params &&
                    l.params.on &&
                    Object.keys(l.params.on).forEach((e) => {
                        l.on(e, l.params.on[e]);
                    }),
                l.params && l.params.onAny && l.onAny(l.params.onAny),
                Object.assign(l, {
                    enabled: l.params.enabled,
                    el: e,
                    classNames: [],
                    slides: [],
                    slidesGrid: [],
                    snapGrid: [],
                    slidesSizesGrid: [],
                    isHorizontal: () => "horizontal" === l.params.direction,
                    isVertical: () => "vertical" === l.params.direction,
                    activeIndex: 0,
                    realIndex: 0,
                    isBeginning: !0,
                    isEnd: !1,
                    translate: 0,
                    previousTranslate: 0,
                    progress: 0,
                    velocity: 0,
                    animating: !1,
                    cssOverflowAdjustment() {
                        return Math.trunc(this.translate / 2 ** 23) * 2 ** 23;
                    },
                    allowSlideNext: l.params.allowSlideNext,
                    allowSlidePrev: l.params.allowSlidePrev,
                    touchEventsData: {
                        isTouched: void 0,
                        isMoved: void 0,
                        allowTouchCallbacks: void 0,
                        touchStartTime: void 0,
                        isScrolling: void 0,
                        currentTranslate: void 0,
                        startTranslate: void 0,
                        allowThresholdMove: void 0,
                        focusableElements: l.params.focusableElements,
                        lastClickTime: 0,
                        clickTimeout: void 0,
                        velocities: [],
                        allowMomentumBounce: void 0,
                        startMoving: void 0,
                        pointerId: null,
                        touchId: null,
                    },
                    allowClick: !0,
                    allowTouchMove: l.params.allowTouchMove,
                    touches: { startX: 0, startY: 0, currentX: 0, currentY: 0, diff: 0 },
                    imagesToLoad: [],
                    imagesLoaded: 0,
                }),
                l.emit("_swiper"),
                l.params.init && l.init(),
                l
            );
        }
        getDirectionLabel(e) {
            return this.isHorizontal()
                ? e
                : {
                    width: "height",
                    "margin-top": "margin-left",
                    "margin-bottom ": "margin-right",
                    "margin-left": "margin-top",
                    "margin-right": "margin-bottom",
                    "padding-left": "padding-top",
                    "padding-right": "padding-bottom",
                    marginRight: "marginBottom",
                }[e];
        }
        getSlideIndex(e) {
            const { slidesEl: t, params: s } = this,
                i = g(m(t, `.${s.slideClass}, swiper-slide`)[0]);
            return g(e) - i;
        }
        getSlideIndexByData(e) {
            return this.getSlideIndex(this.slides.find((t) => 1 * t.getAttribute("data-swiper-slide-index") === e));
        }
        recalcSlides() {
            const { slidesEl: e, params: t } = this;
            this.slides = m(e, `.${t.slideClass}, swiper-slide`);
        }
        enable() {
            const e = this;
            e.enabled || ((e.enabled = !0), e.params.grabCursor && e.setGrabCursor(), e.emit("enable"));
        }
        disable() {
            const e = this;
            e.enabled && ((e.enabled = !1), e.params.grabCursor && e.unsetGrabCursor(), e.emit("disable"));
        }
        setProgress(e, t) {
            const s = this;
            e = Math.min(Math.max(e, 0), 1);
            const i = s.minTranslate(),
                r = (s.maxTranslate() - i) * e + i;
            s.translateTo(r, void 0 === t ? 0 : t), s.updateActiveIndex(), s.updateSlidesClasses();
        }
        emitContainerClasses() {
            const e = this;
            if (!e.params._emitClasses || !e.el) return;
            const t = e.el.className.split(" ").filter((t) => 0 === t.indexOf("swiper") || 0 === t.indexOf(e.params.containerModifierClass));
            e.emit("_containerClasses", t.join(" "));
        }
        getSlideClasses(e) {
            const t = this;
            return t.destroyed
                ? ""
                : e.className
                    .split(" ")
                    .filter((e) => 0 === e.indexOf("swiper-slide") || 0 === e.indexOf(t.params.slideClass))
                    .join(" ");
        }
        emitSlidesClasses() {
            const e = this;
            if (!e.params._emitClasses || !e.el) return;
            const t = [];
            e.slides.forEach((s) => {
                const i = e.getSlideClasses(s);
                t.push({ slideEl: s, classNames: i }), e.emit("_slideClass", s, i);
            }),
                e.emit("_slideClasses", t);
        }
        slidesPerViewDynamic(e, t) {
            void 0 === e && (e = "current"), void 0 === t && (t = !1);
            const { params: s, slides: i, slidesGrid: r, slidesSizesGrid: a, size: n, activeIndex: l } = this;
            let o = 1;
            if ("number" == typeof s.slidesPerView) return s.slidesPerView;
            if (s.centeredSlides) {
                let e,
                    t = i[l] ? Math.ceil(i[l].swiperSlideSize) : 0;
                for (let s = l + 1; s < i.length; s += 1) i[s] && !e && ((t += Math.ceil(i[s].swiperSlideSize)), (o += 1), t > n && (e = !0));
                for (let s = l - 1; s >= 0; s -= 1) i[s] && !e && ((t += i[s].swiperSlideSize), (o += 1), t > n && (e = !0));
            } else if ("current" === e) for (let e = l + 1; e < i.length; e += 1) (t ? r[e] + a[e] - r[l] < n : r[e] - r[l] < n) && (o += 1);
            else for (let e = l - 1; e >= 0; e -= 1) r[l] - r[e] < n && (o += 1);
            return o;
        }
        update() {
            const e = this;
            if (!e || e.destroyed) return;
            const { snapGrid: t, params: s } = e;
            function i() {
                const t = e.rtlTranslate ? -1 * e.translate : e.translate,
                    s = Math.min(Math.max(t, e.maxTranslate()), e.minTranslate());
                e.setTranslate(s), e.updateActiveIndex(), e.updateSlidesClasses();
            }
            let r;
            if (
                (s.breakpoints && e.setBreakpoint(),
                [...e.el.querySelectorAll('[loading="lazy"]')].forEach((t) => {
                    t.complete && k(e, t);
                }),
                e.updateSize(),
                e.updateSlides(),
                e.updateProgress(),
                e.updateSlidesClasses(),
                s.freeMode && s.freeMode.enabled && !s.cssMode)
            )
                i(), s.autoHeight && e.updateAutoHeight();
            else {
                if (("auto" === s.slidesPerView || s.slidesPerView > 1) && e.isEnd && !s.centeredSlides) {
                    const t = e.virtual && s.virtual.enabled ? e.virtual.slides : e.slides;
                    r = e.slideTo(t.length - 1, 0, !1, !0);
                } else r = e.slideTo(e.activeIndex, 0, !1, !0);
                r || i();
            }
            s.watchOverflow && t !== e.snapGrid && e.checkOverflow(), e.emit("update");
        }
        changeDirection(e, t) {
            void 0 === t && (t = !0);
            const s = this,
                i = s.params.direction;
            return (
                e || (e = "horizontal" === i ? "vertical" : "horizontal"),
                e === i ||
                    ("horizontal" !== e && "vertical" !== e) ||
                    (s.el.classList.remove(`${s.params.containerModifierClass}${i}`),
                    s.el.classList.add(`${s.params.containerModifierClass}${e}`),
                    s.emitContainerClasses(),
                    (s.params.direction = e),
                    s.slides.forEach((t) => {
                        "vertical" === e ? (t.style.width = "") : (t.style.height = "");
                    }),
                    s.emit("changeDirection"),
                    t && s.update()),
                s
            );
        }
        changeLanguageDirection(e) {
            const t = this;
            (t.rtl && "rtl" === e) ||
                (!t.rtl && "ltr" === e) ||
                ((t.rtl = "rtl" === e),
                (t.rtlTranslate = "horizontal" === t.params.direction && t.rtl),
                t.rtl ? (t.el.classList.add(`${t.params.containerModifierClass}rtl`), (t.el.dir = "rtl")) : (t.el.classList.remove(`${t.params.containerModifierClass}rtl`), (t.el.dir = "ltr")),
                t.update());
        }
        mount(e) {
            const t = this;
            if (t.mounted) return !0;
            let s = e || t.params.el;
            if (("string" == typeof s && (s = document.querySelector(s)), !s)) return !1;
            (s.swiper = t), s.parentNode && s.parentNode.host && s.parentNode.host.nodeName === t.params.swiperElementNodeName.toUpperCase() && (t.isElement = !0);
            const i = () => `.${(t.params.wrapperClass || "").trim().split(" ").join(".")}`;
            let r = s && s.shadowRoot && s.shadowRoot.querySelector ? s.shadowRoot.querySelector(i()) : m(s, i())[0];
            return (
                !r &&
                    t.params.createElements &&
                    ((r = h("div", t.params.wrapperClass)),
                    s.append(r),
                    m(s, `.${t.params.slideClass}`).forEach((e) => {
                        r.append(e);
                    })),
                Object.assign(t, {
                    el: s,
                    wrapperEl: r,
                    slidesEl: t.isElement && !s.parentNode.host.slideSlots ? s.parentNode.host : r,
                    hostEl: t.isElement ? s.parentNode.host : s,
                    mounted: !0,
                    rtl: "rtl" === s.dir.toLowerCase() || "rtl" === v(s, "direction"),
                    rtlTranslate: "horizontal" === t.params.direction && ("rtl" === s.dir.toLowerCase() || "rtl" === v(s, "direction")),
                    wrongRTL: "-webkit-box" === v(r, "display"),
                }),
                !0
            );
        }
        init(e) {
            const t = this;
            if (t.initialized) return t;
            if (!1 === t.mount(e)) return t;
            t.emit("beforeInit"),
                t.params.breakpoints && t.setBreakpoint(),
                t.addClasses(),
                t.updateSize(),
                t.updateSlides(),
                t.params.watchOverflow && t.checkOverflow(),
                t.params.grabCursor && t.enabled && t.setGrabCursor(),
                t.params.loop && t.virtual && t.params.virtual.enabled
                    ? t.slideTo(t.params.initialSlide + t.virtual.slidesBefore, 0, t.params.runCallbacksOnInit, !1, !0)
                    : t.slideTo(t.params.initialSlide, 0, t.params.runCallbacksOnInit, !1, !0),
                t.params.loop && t.loopCreate(void 0, !0),
                t.attachEvents();
            const s = [...t.el.querySelectorAll('[loading="lazy"]')];
            return (
                t.isElement && s.push(...t.hostEl.querySelectorAll('[loading="lazy"]')),
                s.forEach((e) => {
                    e.complete
                        ? k(t, e)
                        : e.addEventListener("load", (e) => {
                              k(t, e.target);
                          });
                }),
                O(t),
                (t.initialized = !0),
                O(t),
                t.emit("init"),
                t.emit("afterInit"),
                t
            );
        }
        destroy(e, t) {
            void 0 === e && (e = !0), void 0 === t && (t = !0);
            const s = this,
                { params: i, el: r, wrapperEl: a, slides: n } = s;
            return (
                void 0 === s.params ||
                    s.destroyed ||
                    (s.emit("beforeDestroy"),
                    (s.initialized = !1),
                    s.detachEvents(),
                    i.loop && s.loopDestroy(),
                    t &&
                        (s.removeClasses(),
                        r && "string" != typeof r && r.removeAttribute("style"),
                        a && a.removeAttribute("style"),
                        n &&
                            n.length &&
                            n.forEach((e) => {
                                e.classList.remove(i.slideVisibleClass, i.slideFullyVisibleClass, i.slideActiveClass, i.slideNextClass, i.slidePrevClass), e.removeAttribute("style"), e.removeAttribute("data-swiper-slide-index");
                            })),
                    s.emit("destroy"),
                    Object.keys(s.eventsListeners).forEach((e) => {
                        s.off(e);
                    }),
                    !1 !== e &&
                        (s.el && "string" != typeof s.el && (s.el.swiper = null),
                        (function (e) {
                            const t = e;
                            Object.keys(t).forEach((e) => {
                                try {
                                    t[e] = null;
                                } catch (e) {}
                                try {
                                    delete t[e];
                                } catch (e) {}
                            });
                        })(s)),
                    (s.destroyed = !0)),
                null
            );
        }
        static extendDefaults(e) {
            c(K, e);
        }
        static get extendedDefaults() {
            return K;
        }
        static get defaults() {
            return X;
        }
        static installModule(e) {
            J.prototype.__modules__ || (J.prototype.__modules__ = []);
            const t = J.prototype.__modules__;
            "function" == typeof e && t.indexOf(e) < 0 && t.push(e);
        }
        static use(e) {
            return Array.isArray(e) ? (e.forEach((e) => J.installModule(e)), J) : (J.installModule(e), J);
        }
    }
    function Q(e, t, s, i) {
        return (
            e.params.createElements &&
                Object.keys(i).forEach((r) => {
                    if (!s[r] && !0 === s.auto) {
                        let a = m(e.el, `.${i[r]}`)[0];
                        a || ((a = h("div", i[r])), (a.className = i[r]), e.el.append(a)), (s[r] = a), (t[r] = a);
                    }
                }),
            s
        );
    }
    function Z(e) { // <-- Definition of Z (Navigation module)
        let { swiper: t, extendParams: s, on: i, emit: r } = e;
        function a(e) {
            let s;
            return e && "string" == typeof e && t.isElement && ((s = t.el.querySelector(e) || t.hostEl.querySelector(e)), s)
                ? s
                : (e &&
                      ("string" == typeof e && (s = [...document.querySelectorAll(e)]),
                      t.params.uniqueNavElements && "string" == typeof e && s && s.length > 1 && 1 === t.el.querySelectorAll(e).length ? (s = t.el.querySelector(e)) : s && 1 === s.length && (s = s[0])),
                  e && !s ? e : s);
        }
        function n(e, s) {
            const i = t.params.navigation;
            (e = b(e)).forEach((e) => {
                e && (e.classList[s ? "add" : "remove"](...i.disabledClass.split(" ")), "BUTTON" === e.tagName && (e.disabled = s), t.params.watchOverflow && t.enabled && e.classList[t.isLocked ? "add" : "remove"](i.lockClass));
            });
        }
        function l() {
            const { nextEl: e, prevEl: s } = t.navigation;
            if (t.params.loop) return n(s, !1), void n(e, !1);
            n(s, t.isBeginning && !t.params.rewind), n(e, t.isEnd && !t.params.rewind);
        }
        function o(e) {
            e.preventDefault(), (!t.isBeginning || t.params.loop || t.params.rewind) && (t.slidePrev(), r("navigationPrev"));
        }
        function d(e) {
            e.preventDefault(), (!t.isEnd || t.params.loop || t.params.rewind) && (t.slideNext(), r("navigationNext"));
        }
        function c() {
            const e = t.params.navigation;
            if (((t.params.navigation = Q(t, t.originalParams.navigation, t.params.navigation, { nextEl: "swiper-button-next", prevEl: "swiper-button-prev" })), !e.nextEl && !e.prevEl)) return;
            let s = a(e.nextEl),
                i = a(e.prevEl);
            Object.assign(t.navigation, { nextEl: s, prevEl: i }), (s = b(s)), (i = b(i));
            const r = (s, i) => {
                s && s.addEventListener("click", "next" === i ? d : o), !t.enabled && s && s.classList.add(...e.lockClass.split(" "));
            };
            s.forEach((e) => r(e, "next")), i.forEach((e) => r(e, "prev"));
        }
        function p() {
            let { nextEl: e, prevEl: s } = t.navigation;
            (e = b(e)), (s = b(s));
            const i = (e, s) => {
                e.removeEventListener("click", "next" === s ? d : o), e.classList.remove(...t.params.navigation.disabledClass.split(" "));
            };
            e.forEach((e) => i(e, "next")), s.forEach((e) => i(e, "prev"));
        }
        s({
            navigation: { nextEl: null, prevEl: null, hideOnClick: !1, disabledClass: "swiper-button-disabled", hiddenClass: "swiper-button-hidden", lockClass: "swiper-button-lock", navigationDisabledClass: "swiper-navigation-disabled" },
        }),
            (t.navigation = { nextEl: null, prevEl: null }),
            i("init", () => {
                !1 === t.params.navigation.enabled ? u() : (c(), l());
            }),
            i("toEdge fromEdge lock unlock", () => {
                l();
            }),
            i("destroy", () => {
                p();
            }),
            i("enable disable", () => {
                let { nextEl: e, prevEl: s } = t.navigation;
                (e = b(e)), (s = b(s)), t.enabled ? l() : [...e, ...s].filter((e) => !!e).forEach((e) => e.classList.add(t.params.navigation.lockClass));
            }),
            i("click", (e, s) => {
                let { nextEl: i, prevEl: a } = t.navigation;
                (i = b(i)), (a = b(a));
                const n = s.target;
                let l = a.includes(n) || i.includes(n);
                if (t.isElement && !l) {
                    const e = s.path || (s.composedPath && s.composedPath());
                    e && (l = e.find((e) => i.includes(e) || a.includes(e)));
                }
                if (t.params.navigation.hideOnClick && !l) {
                    if (t.pagination && t.params.pagination && t.params.pagination.clickable && (t.pagination.el === n || t.pagination.el.contains(n))) return;
                    let e;
                    i.length ? (e = i[0].classList.contains(t.params.navigation.hiddenClass)) : a.length && (e = a[0].classList.contains(t.params.navigation.hiddenClass)),
                        r(!0 === e ? "navigationShow" : "navigationHide"),
                        [...i, ...a].filter((e) => !!e).forEach((e) => e.classList.toggle(t.params.navigation.hiddenClass));
                }
            });
        const u = () => {
            t.el.classList.add(...t.params.navigation.navigationDisabledClass.split(" ")), p();
        };
        Object.assign(t.navigation, {
            enable: () => {
                t.el.classList.remove(...t.params.navigation.navigationDisabledClass.split(" ")), c(), l();
            },
            disable: u,
            update: l,
            init: c,
            destroy: p,
        });
    }
    function ee(e) { // <-- Definition of ee (Scrollbar module)
        let { swiper: t, extendParams: s, on: r, emit: o } = e;
        const d = i();
        let c,
            p,
            u,
            m,
            f = !1,
            v = null,
            g = null;
        function w() {
            if (!t.params.scrollbar.el || !t.scrollbar.el) return;
            const { scrollbar: e, rtlTranslate: s } = t,
                { dragEl: i, el: r } = e,
                a = t.params.scrollbar,
                n = t.params.loop ? t.progressLoop : t.progress;
            let l = p,
                o = (u - p) * n;
            s ? ((o = -o), o > 0 ? ((l = p - o), (o = 0)) : -o + p > u && (l = u + o)) : o < 0 ? ((l = p + o), (o = 0)) : o + p > u && (l = u - o),
                t.isHorizontal() ? ((i.style.transform = `translate3d(${o}px, 0, 0)`), (i.style.width = `${l}px`)) : ((i.style.transform = `translate3d(0px, ${o}px, 0)`), (i.style.height = `${l}px`)),
                a.hide &&
                    (clearTimeout(v),
                    (r.style.opacity = 1),
                    (v = setTimeout(() => {
                        (r.style.opacity = 0), (r.style.transitionDuration = "400ms");
                    }, 1e3)));
        }
        function S() {
            if (!t.params.scrollbar.el || !t.scrollbar.el) return;
            const { scrollbar: e } = t,
                { dragEl: s, el: i } = e;
            (s.style.width = ""),
                (s.style.height = ""),
                (u = t.isHorizontal() ? i.offsetWidth : i.offsetHeight),
                (m = t.size / (t.virtualSize + t.params.slidesOffsetBefore - (t.params.centeredSlides ? t.snapGrid[0] : 0))),
                (p = "auto" === t.params.scrollbar.dragSize ? u * m : parseInt(t.params.scrollbar.dragSize, 10)),
                t.isHorizontal() ? (s.style.width = `${p}px`) : (s.style.height = `${p}px`),
                (i.style.display = m >= 1 ? "none" : ""),
                t.params.scrollbar.hide && (i.style.opacity = 0),
                t.params.watchOverflow && t.enabled && e.el.classList[t.isLocked ? "add" : "remove"](t.params.scrollbar.lockClass);
        }
        function T(e) {
            return t.isHorizontal() ? e.clientX : e.clientY;
        }
        function y(e) {
            const { scrollbar: s, rtlTranslate: r } = t,
                { el: n } = s;
            let l;
            (l =
                (T(e) -
                    (function (e) {
                        const t = a(),
                            s = i(),
                            r = e.getBoundingClientRect(),
                            n = s.body,
                            l = e.clientTop || n.clientTop || 0,
                            o = e.clientLeft || n.clientLeft || 0,
                            d = e === t ? t.scrollY : e.scrollTop,
                            c = e === t ? t.scrollX : e.scrollLeft;
                        return { top: r.top + d - l, left: r.left + c - o };
                    })(n)[t.isHorizontal() ? "left" : "top"] -
                    (null !== c ? c : p / 2)) /
                (u - p)),
                (l = Math.max(Math.min(l, 1), 0)),
                r && (l = 1 - l);
            const o = t.minTranslate() + (t.maxTranslate() - t.minTranslate()) * l;
            t.updateProgress(o), t.setTranslate(o), t.updateActiveIndex(), t.updateSlidesClasses();
        }
        function E(e) {
            const s = t.params.scrollbar,
                { scrollbar: i, wrapperEl: r } = t,
                { el: a, dragEl: n } = i;
            (f = !0),
                (c = e.target === n ? T(e) - e.target.getBoundingClientRect()[t.isHorizontal() ? "left" : "top"] : null),
                e.preventDefault(),
                e.stopPropagation(),
                (r.style.transitionDuration = "100ms"),
                (n.style.transitionDuration = "100ms"),
                y(e),
                clearTimeout(g),
                (a.style.transitionDuration = "0ms"),
                s.hide && (a.style.opacity = 1),
                t.params.cssMode && (t.wrapperEl.style["scroll-snap-type"] = "none"),
                o("scrollbarDragStart", e);
        }
        function x(e) {
            const { scrollbar: s, wrapperEl: i } = t,
                { el: r, dragEl: a } = s;
            f &&
                (e.preventDefault && e.cancelable ? e.preventDefault() : (e.returnValue = !1),
                y(e),
                (i.style.transitionDuration = "0ms"),
                (r.style.transitionDuration = "0ms"),
                (a.style.transitionDuration = "0ms"),
                o("scrollbarDragMove", e));
        }
        function C(e) {
            const s = t.params.scrollbar,
                { scrollbar: i, wrapperEl: r } = t,
                { el: a } = i;
            f &&
                ((f = !1),
                t.params.cssMode && ((t.wrapperEl.style["scroll-snap-type"] = ""), (r.style.transitionDuration = "")),
                s.hide &&
                    (clearTimeout(g),
                    (g = l(() => {
                        (a.style.opacity = 0), (a.style.transitionDuration = "400ms");
                    }, 1e3))),
                o("scrollbarDragEnd", e),
                s.snapOnRelease && t.slideToClosest());
        }
        function M(e) {
            const { scrollbar: s, params: i } = t,
                r = s.el;
            if (!r) return;
            const a = r,
                n = !!i.passiveListeners && { passive: !1, capture: !1 },
                l = !!i.passiveListeners && { passive: !0, capture: !1 };
            if (!a) return;
            const o = "on" === e ? "addEventListener" : "removeEventListener";
            a[o]("pointerdown", E, n), d[o]("pointermove", x, n), d[o]("pointerup", C, l);
        }
        function P() {
            const { scrollbar: e, el: s } = t;
            t.params.scrollbar = Q(t, t.originalParams.scrollbar, t.params.scrollbar, { el: "swiper-scrollbar" });
            const i = t.params.scrollbar;
            if (!i.el) return;
            let r, a;
            if (("string" == typeof i.el && t.isElement && (r = t.el.querySelector(i.el)), r || "string" != typeof i.el)) r || (r = i.el);
            else if (((r = d.querySelectorAll(i.el)), !r.length)) return;
            var l;
            t.params.uniqueNavElements && "string" == typeof i.el && r.length > 1 && 1 === s.querySelectorAll(i.el).length && (r = s.querySelector(i.el)),
                r.length > 0 && (r = r[0]),
                r.classList.add(t.isHorizontal() ? i.horizontalClass : i.verticalClass),
                r &&
                    ((a = r.querySelector(
                        (void 0 === (l = t.params.scrollbar.dragClass) && (l = ""),
                        `.${l
                            .trim()
                            .replace(/([\.:!+\/])/g, "\\$1")
                            .replace(/ /g, ".")}`)
                    )),
                    a || ((a = h("div", t.params.scrollbar.dragClass)), r.append(a))),
                Object.assign(e, { el: r, dragEl: a }),
                i.draggable && t.params.scrollbar.el && t.scrollbar.el && M("on"),
                r && r.classList[t.enabled ? "remove" : "add"](...b(t.params.scrollbar.lockClass)); // Correction: utiliser b()
        }
        function L() {
            const e = t.params.scrollbar,
                s = t.scrollbar.el;
            s && s.classList.remove(...b(t.isHorizontal() ? e.horizontalClass : e.verticalClass)), t.params.scrollbar.el && t.scrollbar.el && M("off"); // Correction: utiliser b()
        }
        s({
            scrollbar: {
                el: null,
                dragSize: "auto",
                hide: !1,
                draggable: !1,
                snapOnRelease: !0,
                lockClass: "swiper-scrollbar-lock",
                dragClass: "swiper-scrollbar-drag",
                scrollbarDisabledClass: "swiper-scrollbar-disabled",
                horizontalClass: "swiper-scrollbar-horizontal",
                verticalClass: "swiper-scrollbar-vertical",
            },
        }),
            (t.scrollbar = { el: null, dragEl: null }),
            r("changeDirection", () => {
                 if (!t.scrollbar || !t.scrollbar.el) return;
                 const e = t.params.scrollbar;
                 let { el: s } = t.scrollbar;
                 s = b(s); // Correction: utiliser b()
                 s.forEach((s) => {
                     s.classList.remove(e.horizontalClass, e.verticalClass);
                     s.classList.add(t.isHorizontal() ? e.horizontalClass : e.verticalClass);
                 });
             }),
            r("init", () => {
                !1 === t.params.scrollbar.enabled ? k() : (P(), S(), w());
            }),
            r("update resize observerUpdate lock unlock changeDirection", () => {
                S();
            }),
            r("setTranslate", () => {
                w();
            }),
            r("setTransition", (e, s) => {
                !(function (e) {
                    t.params.scrollbar.el && t.scrollbar.el && (t.scrollbar.dragEl.style.transitionDuration = `${e}ms`);
                })(s);
            }),
            r("enable disable", () => {
                const { el: e } = t.scrollbar;
                e && e.classList[t.enabled ? "remove" : "add"](...b(t.params.scrollbar.lockClass)); // Correction: utiliser b()
            }),
            r("destroy", () => {
                L();
            });
        const k = () => {
             t.el.classList.add(...b(t.params.scrollbar.scrollbarDisabledClass)); // Correction: utiliser b()
             t.scrollbar.el && t.scrollbar.el.classList.add(...b(t.params.scrollbar.scrollbarDisabledClass)); // Correction: utiliser b()
             L();
         };
        Object.assign(t.scrollbar, {
            enable: () => {
                t.el.classList.remove(...b(t.params.scrollbar.scrollbarDisabledClass)); // Correction: utiliser b()
                t.scrollbar.el && t.scrollbar.el.classList.remove(...b(t.params.scrollbar.scrollbarDisabledClass)); // Correction: utiliser b()
                P(), S(), w();
            },
            disable: k,
            updateSize: S,
            setTranslate: w,
            init: P,
            destroy: L,
        });
    }
    Object.keys(U).forEach((e) => {
        Object.keys(U[e]).forEach((t) => {
            J.prototype[t] = U[e][t];
        });
    }),
        J.use([ // Modules Swiper utilisés
            function (e) {
                let { swiper: t, on: s, emit: i } = e;
                const r = a();
                let n = null,
                    l = null;
                const o = () => {
                        t && !t.destroyed && t.initialized && (i("beforeResize"), i("resize"));
                    },
                    d = () => {
                        t && !t.destroyed && t.initialized && i("orientationchange");
                    };
                s("init", () => {
                    t.params.resizeObserver && void 0 !== r.ResizeObserver
                        ? t &&
                          !t.destroyed &&
                          t.initialized &&
                          ((n = new ResizeObserver((e) => {
                              l = r.requestAnimationFrame(() => {
                                  const { width: s, height: i } = t;
                                  let r = s,
                                      a = i;
                                  e.forEach((e) => {
                                      let { contentBoxSize: s, contentRect: i, target: n } = e;
                                      (n && n !== t.el) || ((r = i ? i.width : (s[0] || s).inlineSize), (a = i ? i.height : (s[0] || s).blockSize));
                                  }),
                                      (r === s && a === i) || o();
                              });
                          })),
                          n.observe(t.el))
                        : (r.addEventListener("resize", o), r.addEventListener("orientationchange", d));
                }),
                    s("destroy", () => {
                        l && r.cancelAnimationFrame(l), n && n.unobserve && t.el && (n.unobserve(t.el), (n = null)), r.removeEventListener("resize", o), r.removeEventListener("orientationchange", d);
                    });
            },
            function (e) {
                let { swiper: t, extendParams: s, on: i, emit: r } = e;
                const n = [],
                    l = a(),
                    o = function (e, s) {
                        void 0 === s && (s = {});
                        const i = new (l.MutationObserver || l.WebkitMutationObserver)((e) => {
                            if (t.__preventObserver__) return;
                            if (1 === e.length) return void r("observerUpdate", e[0]);
                            const s = function () {
                                r("observerUpdate", e[0]);
                            };
                            l.requestAnimationFrame ? l.requestAnimationFrame(s) : l.setTimeout(s, 0);
                        });
                        i.observe(e, { attributes: void 0 === s.attributes || s.attributes, childList: t.isElement || (void 0 === s.childList || s).childList, characterData: void 0 === s.characterData || s.characterData }), n.push(i);
                    };
                s({ observer: !1, observeParents: !1, observeSlideChildren: !1 }),
                    i("init", () => {
                        if (t.params.observer) {
                            if (t.params.observeParents) {
                                const e = (function (e) {
                                    const t = [];
                                    let s = e.parentElement;
                                    for (; s; ) t.push(s), (s = s.parentElement);
                                    return t;
                                })(t.hostEl);
                                for (let t = 0; t < e.length; t += 1) o(e[t]);
                            }
                            o(t.hostEl, { childList: t.params.observeSlideChildren }), o(t.wrapperEl, { attributes: !1 });
                        }
                    }),
                    i("destroy", () => {
                        n.forEach((e) => {
                            e.disconnect();
                        }),
                            n.splice(0, n.length);
                    });
            },
        ]);

    // --- END: Minified Swiper Code ---


    // ===== START: CORRECTLY PLACED Swiper Initialization Block =====
    document.addEventListener("DOMContentLoaded", function () {
        // Initialisation pour .hits__slider
        try {
            if (document.querySelector(".hits__slider")) {
                new J(".hits__slider", { // J should be defined now
                    modules: [Z],      // Z should be defined now
                    spaceBetween: 20,
                    rewind: !0,
                    slidesPerView: 1.4,
                    navigation: { nextEl: "#hits-right", prevEl: "#hits-left" },
                    breakpoints: { 576: { slidesPerView: 1.8 }, 768: { slidesPerView: 2.5, spaceBetween: 16 }, 1024: { slidesPerView: 3 }, 1200: { slidesPerView: 4.5 } },
                    slideClass: "hits__slider-slide",
                    wrapperClass: "hits__slider-wrapper",
                });
            }
        } catch (error) {
            console.error("Erreur lors de l'initialisation du slider 'hits__slider':", error);
        }

        // Initialisation pour .promo__slider
        try {
            if (document.querySelector(".promo__slider")) {
                new J(".promo__slider", { // J should be defined
                    modules: [Z],       // Z should be defined
                    spaceBetween: 20,
                    rewind: !0,
                    slidesPerView: 1,
                    navigation: { nextEl: "#promo-left", prevEl: "#promo-right" },
                    breakpoints: { 768: { slidesPerView: 1.2, spaceBetween: 16 }, 1024: { slidesPerView: 1.5 }, 1200: { slidesPerView: 1.8 } },
                    slideClass: "promo__slider-slide",
                    wrapperClass: "promo__slider-wrapper",
                });
            }
        } catch (error) {
            console.error("Erreur lors de l'initialisation du slider 'promo__slider':", error);
        }

        // Initialisation pour .card__images-slider
        try {
            if (document.querySelector(".card__images-slider")) {
                new J(".card__images-slider", { // J should be defined
                    modules: [ee],            // ee should be defined
                    spaceBetween: 10,
                    direction: "vertical",
                    scrollbar: { el: ".swiper-scrollbar", draggable: !0, hide: !1, snapOnRelease: !0 },
                    rewind: !0,
                    slidesPerView: 2.2,
                    breakpoints: { 768: { slidesPerView: 2.5, spaceBetween: 15 }, 1024: { slidesPerView: 3.5 }, 1200: { slidesPerView: 3.5 } },
                    slideClass: "card__images-slider__slide ",
                    wrapperClass: "card__images-slider__wrapper",
                });
            }
        } catch (error) {
            console.error("Erreur lors de l'initialisation du slider 'card__images-slider':", error);
        }
    });
    // ===== END: CORRECTLY PLACED Swiper Initialization Block =====

})();
// ========================================
// END: Contenu de sliders.txt
// ========================================


// ========================================
// START: Contenu de main.txt (Logique principale, Modales, Tabs, Header dynamique)
// ========================================
(() => {
    "use strict";
    // Fonction utilitaire pour les modales
    let scrollPosition = 0;
    let scrollbarWidth = 0;

    function getScrollbarWidth() {
        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.overflow = 'scroll';
        document.body.appendChild(outer);
        
        const inner = document.createElement('div');
        outer.appendChild(inner);
        
        scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
        
        outer.parentNode.removeChild(outer);
        return scrollbarWidth;
    }

    function lockScroll() {
        scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        scrollbarWidth = getScrollbarWidth();
        
        document.body.style.setProperty('--scrollbar-width', `${scrollbarWidth}px`);
        document.body.style.top = `-${scrollPosition}px`;
        document.body.classList.add('body-no-scroll');
    }

    function unlockScroll() {
        document.body.classList.remove('body-no-scroll');
        document.body.style.removeProperty('top');
        document.body.style.removeProperty('--scrollbar-width');
        window.scrollTo({ top: scrollPosition, behavior: 'instant' });
    }

    function setupModal(modalSelector, closeSelector, openTriggers = null) {
        getScrollbarWidth();
        
        const modalElement = document.querySelector(modalSelector);
        const closeButton = document.querySelector(closeSelector);
        const overlay = document.querySelector(".overlay");

        function openModal() {
            lockScroll();
            modalElement?.classList.add("show");
            overlay?.classList.add("show");
        }

        function closeModal() {
            modalElement?.classList.remove("show");
            overlay?.classList.remove("show");
            setTimeout(unlockScroll, 10);
        }

        closeButton?.addEventListener("click", closeModal);
        overlay?.addEventListener("click", closeModal);
        modalElement?.addEventListener("click", (e) => e.target === modalElement && closeModal());

        if (openTriggers) {
            const triggers = Array.isArray(openTriggers) ? openTriggers : [openTriggers];
            triggers.forEach(trigger => {
                document.querySelectorAll(trigger).forEach(btn => {
                    btn?.addEventListener("click", openModal);
                });
            });
        }
    }    
    
    document.addEventListener("DOMContentLoaded", function () {
        // Initialisation des modales
        try {
            setupModal(".modal-recall", ".modal__close-recall", ['[data-open="recall"]', '[data-open="recall-mobile"]']);
            // setupModal(".modal-recall", ".modal__close-recall", ['[data-open="recall"]', '[data-open="recall-mobile"]', '[data-open="recall-service-1"]', '[data-open="recall-service-2"]']);
            setupModal(".catalog-mobile", ".menu-mobile__close", '[data-open="mobile-menu"]');
            setupModal(".modal-feedback", ".modal__close-feedback", '[data-open="feedback"]');
            setupModal(".modal-buy", ".modal__close-buy", 'button[data-open="buy"]');
            setupModal(".modal-service", ".modal__close-service", 'button[data-open="service"]');
        } catch (error) {
            console.error("Erreur lors de l'initialisation des modales:", error);
        }

        // ***************************************************************
        // ***** NOUVELLE LOGIQUE MENU DROPDOWN (AVEC DELAI) *****
        // ***************************************************************
        // try {
        //     const catalogLink = document.querySelector(".nav-catalog-trigger");
        //     const menuContainer = document.getElementById("menu-dropdown-container");
        //     const menuContentWrapper = document.getElementById("menu-dropdown-content-wrapper");
        //     const menuLoader = menuContentWrapper?.querySelector(".menu-loader");
        
        //     let menuHoverTimer;
        //     const menuHideDelay = 250;
        //     let isMenuContentLoaded = false;
        //     let isMenuFetchInProgress = false;
        
        //     function setupMenuTabs(menuElement) {
        //         if (!menuElement) return;
        //         const tabs = menuElement.querySelectorAll('.menu__tabs .tablink');
        //         const contents = menuElement.querySelectorAll('.menu__content .tabcontent');
        
        //         tabs.forEach(tab => {
        //             tab.addEventListener('mouseenter', function () {
        //                 tabs.forEach(t => t.classList.remove('active'));
        //                 contents.forEach(c => c.classList.remove('active'));
        //                 this.classList.add('active');
        //                 const targetId = this.dataset.target;
        //                 if (targetId) {
        //                     const targetContent = menuElement.querySelector('#' + targetId);
        //                     if (targetContent) targetContent.classList.add('active');
        //                 }
        //             });
        //         });
        
        //         // Active le premier onglet/contenu si aucun n'est actif
        //         if (!menuElement.querySelector('.menu__tabs .tablink.active') && tabs.length > 0) {
        //             tabs[0].classList.add('active');
        //             const firstContentId = tabs[0].dataset.target;
        //             if (firstContentId) {
        //                 const firstContent = menuElement.querySelector('#' + firstContentId);
        //                 if (firstContent) firstContent.classList.add('active');
        //             }
        //         }
        //     }
        
        //     if (catalogLink && menuContainer && menuContentWrapper) {
        //         const fetchAndDisplayMenuContent = async () => {
        //             if (isMenuContentLoaded || isMenuFetchInProgress) return;
        //             if (!catalogLink.dataset.menuContentUrl) return;
        
        //             isMenuFetchInProgress = true;
        //             if (menuLoader) menuLoader.style.display = 'block';
        
        //             try {
        //                 const response = await fetch(catalogLink.dataset.menuContentUrl, {
        //                     headers: { 'X-Requested-With': 'XMLHttpRequest' }
        //                 });
        //                 if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        //                 const htmlContent = await response.text();
        
        //                 menuContentWrapper.innerHTML = htmlContent;
        //                 isMenuContentLoaded = true;
        
        //                 const loadedMenuElement = menuContentWrapper.querySelector('.menu');
        //                 if (loadedMenuElement) {
        //                     setupMenuTabs(loadedMenuElement);
        //                     loadedMenuElement.classList.add('opened');
        //                 }
        //             } catch (error) {
        //                 if (menuContentWrapper) menuContentWrapper.innerHTML = "<p style='padding:20px; color:red;'>Ошибка загрузки меню.</p>";
        //             } finally {
        //                 if (menuLoader) menuLoader.style.display = 'none';
        //                 isMenuFetchInProgress = false;
        //             }
        //         };
        
        //         const showMenu = () => {
        //             clearTimeout(menuHoverTimer);
        //             if (!isMenuContentLoaded && !isMenuFetchInProgress) {
        //                 fetchAndDisplayMenuContent();
        //             }
        //             menuContainer.classList.add("opened");
        //             catalogLink.classList.add("hovered");
        //             catalogLink.setAttribute('aria-expanded', 'true');
        //             menuContainer.setAttribute('aria-hidden', 'false');
        //             // Toujours s'assurer que .menu.opened est présent
        //             const menuDiv = menuContentWrapper.querySelector('.menu');
        //             if (menuDiv) menuDiv.classList.add('opened');
        //         };
        
        //         const startHideTimer = () => {
        //             clearTimeout(menuHoverTimer);
        //             menuHoverTimer = setTimeout(() => {
        //                 menuContainer.classList.remove("opened");
        //                 catalogLink.classList.remove("hovered");
        //                 catalogLink.setAttribute('aria-expanded', 'false');
        //                 menuContainer.setAttribute('aria-hidden', 'true');
        //                 const menuDiv = menuContentWrapper.querySelector('.menu');
        //                 if (menuDiv) menuDiv.classList.remove('opened');
        //             }, menuHideDelay);
        //         };
        
        //         catalogLink.addEventListener("mouseenter", showMenu);
        //         menuContainer.addEventListener("mouseenter", () => {
        //             clearTimeout(menuHoverTimer);
        //             const menuDiv = menuContentWrapper.querySelector('.menu');
        //             if (menuDiv) menuDiv.classList.add('opened');
        //         });
        //         catalogLink.addEventListener("mouseleave", startHideTimer);
        //         menuContainer.addEventListener("mouseleave", startHideTimer);
        //         catalogLink.addEventListener('focus', showMenu);
        
        //     }
        // } catch (error) {
        //     console.error("Error in main dropdown menu logic:", error);
        // }

        // try {
        //     const catalogLink = document.querySelector(".nav-catalog-trigger");
        //     const menuContainer = document.getElementById("menu-dropdown-container");
        //     const menuContentWrapper = document.getElementById("menu-dropdown-content-wrapper");
        //     const menuLoader = menuContentWrapper?.querySelector(".menu-loader");
        
        //     let menuHoverTimer;
        //     const menuHideDelay = 250;
        //     let isMenuContentLoaded = false;
        //     let isMenuFetchInProgress = false;
        
        //     // Nouvelle fonction pour le menu à 3 colonnes
        //     function setupMegaMenuColumns(menuElement) {
        //       if (!menuElement) return;
        
        //       // Niveau 1 -> Niveau 2
        //       const l1Links = menuElement.querySelectorAll('.l1-link');
        //       const l2Columns = menuElement.querySelectorAll('.menu__column--l2');
        //       l1Links.forEach(link => {
        //         link.addEventListener('mouseenter', function() {
        //           l1Links.forEach(l => l.classList.remove('active'));
        //           l2Columns.forEach(col => col.classList.remove('active'));
        //           this.classList.add('active');
        //           const target = this.dataset.target;
        //           if (target) {
        //             const col = menuElement.querySelector('.menu__column--l2.' + target);
        //             if (col) col.classList.add('active');
        //           }
        //           // Masquer les colonnes l3
        //           menuElement.querySelectorAll('.menu__column--l3').forEach(col => col.classList.remove('active'));
        //         });
        //       });
        
        //       // Niveau 2 -> Niveau 3
        //       const l2Links = menuElement.querySelectorAll('.l2-link');
        //       const l3Columns = menuElement.querySelectorAll('.menu__column--l3');
        //       l2Links.forEach(link => {
        //         link.addEventListener('mouseenter', function() {
        //           l2Links.forEach(l => l.classList.remove('active'));
        //           l3Columns.forEach(col => col.classList.remove('active'));
        //           this.classList.add('active');
        //           const target = this.dataset.target;
        //           if (target) {
        //             const col = menuElement.querySelector('.menu__column--l3.' + target);
        //             if (col) col.classList.add('active');
        //           }
        //         });
        //       });
        //     }
        
        //     if (catalogLink && menuContainer && menuContentWrapper) {
        //         const fetchAndDisplayMenuContent = async () => {
        //             if (isMenuContentLoaded || isMenuFetchInProgress) return;
        //             if (!catalogLink.dataset.menuContentUrl) return;
        
        //             isMenuFetchInProgress = true;
        //             if (menuLoader) menuLoader.style.display = 'block';
        
        //             try {
        //                 const response = await fetch(catalogLink.dataset.menuContentUrl, {
        //                     headers: { 'X-Requested-With': 'XMLHttpRequest' }
        //                 });
        //                 if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        //                 const htmlContent = await response.text();
        
        //                 menuContentWrapper.innerHTML = htmlContent;
        //                 isMenuContentLoaded = true;
        
        //                 // Initialisation du menu à 3 colonnes après AJAX
        //                 const loadedMenuElement = menuContentWrapper.querySelector('.menu');
        //                 if (loadedMenuElement) {
        //                     setupMegaMenuColumns(loadedMenuElement);
        //                     loadedMenuElement.classList.add('opened');
        //                 }
        //             } catch (error) {
        //                 if (menuContentWrapper) menuContentWrapper.innerHTML = "<p style='padding:20px; color:red;'>Ошибка загрузки меню.</p>";
        //             } finally {
        //                 if (menuLoader) menuLoader.style.display = 'none';
        //                 isMenuFetchInProgress = false;
        //             }
        //         };
        
        //         // Le reste de ton code pour showMenu et startHideTimer reste identique
        //         const showMenu = () => {
        //             clearTimeout(menuHoverTimer);
        //             if (!isMenuContentLoaded && !isMenuFetchInProgress) {
        //                 fetchAndDisplayMenuContent();
        //             }
        //             menuContainer.classList.add("opened");
        //             catalogLink.classList.add("hovered");
        //             catalogLink.setAttribute('aria-expanded', 'true');
        //             menuContainer.setAttribute('aria-hidden', 'false');
        //             const menuDiv = menuContentWrapper.querySelector('.menu');
        //             if (menuDiv) menuDiv.classList.add('opened');
        //         };
        
        //         const startHideTimer = () => {
        //             clearTimeout(menuHoverTimer);
        //             menuHoverTimer = setTimeout(() => {
        //                 menuContainer.classList.remove("opened");
        //                 catalogLink.classList.remove("hovered");
        //                 catalogLink.setAttribute('aria-expanded', 'false');
        //                 menuContainer.setAttribute('aria-hidden', 'true');
        //                 const menuDiv = menuContentWrapper.querySelector('.menu');
        //                 if (menuDiv) menuDiv.classList.remove('opened');
        //             }, menuHideDelay);
        //         };
        
        //         catalogLink.addEventListener("mouseenter", showMenu);
        //         menuContainer.addEventListener("mouseenter", () => clearTimeout(menuHoverTimer));
        //         catalogLink.addEventListener("mouseleave", startHideTimer);
        //         menuContainer.addEventListener("mouseleave", startHideTimer);
        //         catalogLink.addEventListener('focus', showMenu);
        //     }
        // } catch (error) {
        //     console.error("Error in main dropdown menu logic:", error);
        // }
                        



        try {
            const catalogLink = document.querySelector(".nav-catalog-trigger");
            const menuContainer = document.getElementById("menu-dropdown-container");
            const menuContentWrapper = document.getElementById("menu-dropdown-content-wrapper");
            const menuLoader = menuContentWrapper?.querySelector(".menu-loader");
        
            let menuHoverTimer;
            const menuHideDelay = 250;
            let isMenuContentLoaded = false;
            let isMenuFetchInProgress = false;
        
            function setupMegaMenuColumns(menuElement) {
                if (!menuElement) return;
        
                // Niveau 1 -> Niveau 2
                const l1Links = menuElement.querySelectorAll('.l1-link');
                const l2Columns = menuElement.querySelectorAll('.menu__column--l2');
                const l3Columns = menuElement.querySelectorAll('.menu__column--l3');
        
                l1Links.forEach(link => {
                    link.addEventListener('mouseenter', function() {
                        // Active colonne l2 correspondante
                        l1Links.forEach(l => l.classList.remove('active'));
                        l2Columns.forEach(col => col.classList.remove('active'));
                        l3Columns.forEach(col => col.classList.remove('active')); // Masque tjs l3 au changement de l1
        
                        this.classList.add('active');
                        const target = this.dataset.target;
                        if (target) {
                            const col = menuElement.querySelector('.menu__column--l2.' + target);
                            if (col) col.classList.add('active');
                        }
                    });
                });
        
                // Niveau 2 -> Niveau 3
                const l2Links = menuElement.querySelectorAll('.l2-link');
                l2Links.forEach(link => {
                    link.addEventListener('mouseenter', function() {
                        l2Links.forEach(l => l.classList.remove('active'));
                        l3Columns.forEach(col => col.classList.remove('active'));
                        this.classList.add('active');
                        const target = this.dataset.target;
                        if (target) {
                            const col = menuElement.querySelector('.menu__column--l3.' + target);
                            if (col) col.classList.add('active');
                        }
                    });
                    link.addEventListener('mouseleave', function() {
                        // Optionnel : si tu veux que la colonne l3 disparaisse dès qu'on quitte le l2-link
                        // l3Columns.forEach(col => col.classList.remove('active'));
                        // l2Links.forEach(l => l.classList.remove('active'));
                    });
                });
            }
        
            if (catalogLink && menuContainer && menuContentWrapper) {
                const fetchAndDisplayMenuContent = async () => {
                    if (isMenuContentLoaded || isMenuFetchInProgress) return;
                    if (!catalogLink.dataset.menuContentUrl) return;
        
                    isMenuFetchInProgress = true;
                    if (menuLoader) menuLoader.style.display = 'block';
        
                    try {
                        const response = await fetch(catalogLink.dataset.menuContentUrl, {
                            headers: { 'X-Requested-With': 'XMLHttpRequest' }
                        });
                        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
                        const htmlContent = await response.text();
        
                        menuContentWrapper.innerHTML = htmlContent;
                        isMenuContentLoaded = true;
        
                        // Initialisation du menu à 3 colonnes après AJAX
                        const loadedMenuElement = menuContentWrapper.querySelector('.menu');
                        if (loadedMenuElement) {
                            setupMegaMenuColumns(loadedMenuElement);
                            loadedMenuElement.classList.add('opened');
                        }
                    } catch (error) {
                        if (menuContentWrapper) menuContentWrapper.innerHTML = "<p style='padding:20px; color:red;'>Ошибка загрузки меню.</p>";
                    } finally {
                        if (menuLoader) menuLoader.style.display = 'none';
                        isMenuFetchInProgress = false;
                    }
                };
        
                const showMenu = () => {
                    clearTimeout(menuHoverTimer);
                    if (!isMenuContentLoaded && !isMenuFetchInProgress) {
                        fetchAndDisplayMenuContent();
                    }
                    menuContainer.classList.add("opened");
                    catalogLink.classList.add("hovered");
                    catalogLink.setAttribute('aria-expanded', 'true');
                    menuContainer.setAttribute('aria-hidden', 'false');
                    const menuDiv = menuContentWrapper.querySelector('.menu');
                    if (menuDiv) menuDiv.classList.add('opened');
                };
        
                const startHideTimer = () => {
                    clearTimeout(menuHoverTimer);
                    menuHoverTimer = setTimeout(() => {
                        menuContainer.classList.remove("opened");
                        catalogLink.classList.remove("hovered");
                        catalogLink.setAttribute('aria-expanded', 'false');
                        menuContainer.setAttribute('aria-hidden', 'true');
                        const menuDiv = menuContentWrapper.querySelector('.menu');
                        if (menuDiv) menuDiv.classList.remove('opened');
                    }, menuHideDelay);
                };
        
                catalogLink.addEventListener("mouseenter", showMenu);
                menuContainer.addEventListener("mouseenter", () => clearTimeout(menuHoverTimer));
                catalogLink.addEventListener("mouseleave", startHideTimer);
                menuContainer.addEventListener("mouseleave", startHideTimer);
                catalogLink.addEventListener('focus', showMenu);
            }
        } catch (error) {
            console.error("Error in main dropdown menu logic:", error);
        }
        
        
        // ***************************************************************
        // ***** FIN NOUVELLE LOGIQUE MENU DROPDOWN *****
        // ***************************************************************









        // Logique des onglets (Tabs)
        try {
            const tabLinks = document.querySelectorAll(".tablink");
            if (tabLinks.length > 0) {
                tabLinks.forEach((tabLink) => {
                    tabLink.addEventListener("mouseenter", (event) => {
                        const targetId = tabLink.getAttribute("data-target");
                        if (targetId) {
                            function switchTab(currentEvent, targetContentId) {
                                let allTabLinks = document.querySelectorAll(".tablink");
                                document.querySelectorAll(".tabcontent").forEach(function (tabContent) {
                                    tabContent.classList.remove("active");
                                });
                                allTabLinks.forEach(function (link) {
                                    link.classList.remove("active");
                                });
                                const targetElement = document.getElementById(targetContentId);
                                if (targetElement) {
                                    targetElement.classList.add("active");
                                } else {
                                     console.warn("Contenu d'onglet non trouvé pour l'ID:", targetContentId);
                                }
                                if (currentEvent.currentTarget) {
                                   currentEvent.currentTarget.classList.add("active");
                                }
                            }
                            switchTab(event, targetId);
                        } else {
                           console.warn("Attribut 'data-target' manquant sur .tablink:", tabLink);
                        }
                    });
                });
            }
        } catch(error) {
             console.error("Erreur dans la logique des onglets:", error);
        }

        // Header dynamique au scroll
        try {
            const scrollThreshold = window.innerHeight / 2;
            const dynamicHeader = document.querySelector(".dynamic__header");
            if (dynamicHeader) {
                let isScrolling = null;
                 window.addEventListener("scroll", function () {
                    if (isScrolling) {
                        clearTimeout(isScrolling);
                    }
                    isScrolling = setTimeout(() => {
                         try {
                            if (window.scrollY > scrollThreshold) {
                                 dynamicHeader.classList.add("show");
                            } else {
                                 dynamicHeader.classList.remove("show");
                            }
                         } catch (scrollError) {
                             console.error("Erreur pendant le scroll (timeout):", scrollError);
                         }
                          isScrolling = null;
                    }, 100);
                }, { passive: true });
            }
        } catch(error) {
             console.error("Erreur lors de l'initialisation du header dynamique:", error);
        }

    });
})();
// ========================================
// END: Contenu de main.txt
// ========================================


// ========================================
// START: Contenu de accordion.txt
// ========================================
document.addEventListener("DOMContentLoaded", function () {
    try {
        const rows = document.querySelectorAll(".stages__table-row");
        if (rows.length > 0) {
            rows.forEach((row) => {
                row.addEventListener("click", function () {
                    try {
                        let textElement = this.querySelector(".text p");
                        if (textElement) {
                            textElement.classList.toggle("opened");
                        }
                    } catch (clickError) {
                         console.error("Erreur au clic sur .stages__table-row:", clickError);
                    }
                });
            });
        }
    } catch (error) {
         console.error("Erreur lors de l'initialisation de l'accordéon:", error);
    }
});
// ========================================
// END: Contenu de accordion.txt
// ========================================


// ========================================
// START: Contenu de product.txt (Galerie produit + Logique quantité produit)
// ========================================
document.addEventListener("DOMContentLoaded", function () {
    // Logique de la galerie d'images produit
    try {
        let thumbnails = document.querySelectorAll(".card__images-slider__slide img");
        let mainImage = document.querySelector(".card__images-picture img");

        if (thumbnails.length > 0 && mainImage) {
            thumbnails.forEach((thumb) => {
                thumb.addEventListener("click", function () {
                    try {
                        mainImage.src = this.src;
                    } catch(clickError) {
                        console.error("Erreur au clic sur la miniature produit:", clickError);
                    }
                });
            });
        }
    } catch (error) {
        console.error("Erreur lors de l'initialisation de la galerie produit:", error);
    }

    // Logique de quantité pour la page produit
    try {
        const amountInput = document.getElementById("amount");
        const leftCtrl = document.querySelector(".amount-controls.left");
        const rightCtrl = document.querySelector(".amount-controls.right");

        if (amountInput && leftCtrl && rightCtrl) {
            leftCtrl.addEventListener("click", function () {
                let currentValue = parseInt(amountInput.value, 10);
                if (isNaN(currentValue)) currentValue = 1;
                if (currentValue > 1) {
                    amountInput.value = currentValue - 1;
                    amountInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            rightCtrl.addEventListener("click", function () {
                let currentValue = parseInt(amountInput.value, 10);
                if (isNaN(currentValue)) currentValue = 1;
                if (currentValue < 99) {
                    amountInput.value = currentValue + 1;
                    amountInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            amountInput.addEventListener("input", function () {
                let value = this.value;
                value = value.replace(/\D/g, "");
                if (value === "") {
                    return;
                }
                let numericValue = parseInt(value, 10);

                if (isNaN(numericValue) || numericValue < 1) {
                   // Correction au blur
                } else if (numericValue > 99) {
                    this.value = 99;
                }
            });

            amountInput.addEventListener("blur", function () {
                let numericValue = parseInt(this.value.replace(/\D/g, ""), 10);
                if (isNaN(numericValue) || numericValue < 1) {
                    this.value = 1;
                } else if (numericValue > 99) {
                    this.value = 99;
                } else {
                    this.value = numericValue;
                }
                amountInput.dispatchEvent(new Event('change', { bubbles: true }));
            });
        }
    } catch (error) {
        console.error("Erreur lors de l'initialisation de la logique quantité produit:", error);
    }
});
// ========================================
// END: Contenu de product.txt
// ========================================

// ========================================
// START: Contenu de service.txt (Afficher/Masquer description service)
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing Service Card Toggles...");

    const allServiceCards = document.querySelectorAll('.service-card');

    allServiceCards.forEach(card => {
        const header = card.querySelector('.service-card__header');
        const toggleButton = card.querySelector('.service-card__toggle');

        const handleToggle = (event) => {
            if (event.target.closest('.service-card__button')) {
                console.log("Clicked on order button, ignoring toggle.");
                return;
            }

            if (event.target === toggleButton) {
                event.stopPropagation();
            }

            const currentCard = event.currentTarget.closest('.service-card');
            if (!currentCard) return;

            const isActive = currentCard.classList.contains('active');

            console.log(`Toggling card: ${currentCard.querySelector('.service-card__title')?.textContent}. Currently active: ${isActive}`);

            allServiceCards.forEach(otherCard => {
                if (otherCard !== currentCard) {
                    otherCard.classList.remove('active');
                    const otherToggle = otherCard.querySelector('.service-card__toggle');
                    if (otherToggle) {
                        otherToggle.textContent = 'Подробнее';
                    }
                }
            });

            if (isActive) {
                currentCard.classList.remove('active');
                if (toggleButton) toggleButton.textContent = 'Подробнее';
            } else {
                currentCard.classList.add('active');
                if (toggleButton) toggleButton.textContent = 'Свернуть';
            }
        };

        if (header) {
            header.addEventListener('click', handleToggle);
            header.style.cursor = 'pointer';
        }

        if (toggleButton) {
            toggleButton.addEventListener('click', handleToggle);
            toggleButton.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleToggle(e);
                }
            });
        }
    });
    console.log("Service Card Toggles Initialized.");
});
// ========================================
// END: Contenu de service.txt
// ========================================


document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing Promo Card Toggles...");

    const allPromoCards = document.querySelectorAll('.promo-card');

    allPromoCards.forEach(card => {
        const header = card.querySelector('.promo-card__header');
        const toggleButton = card.querySelector('.promo-card__toggle');
        const content = card.querySelector('.promo-card__content');
        const contentInner = card.querySelector('.promo-card__content-inner');

        // Initial setup
        content.style.transition = 'max-height 0.4s ease-out';
        content.style.overflow = 'hidden';
        content.style.maxHeight = '0';

        const handleToggle = (event) => {
            // Ignore if clicked on other interactive elements
            if (event.target.closest('a, button') && !event.target.closest('.promo-card__toggle')) {
                console.log("Clicked on interactive element, ignoring toggle.");
                return;
            }

            if (event.target === toggleButton) {
                event.stopPropagation();
            }

            const currentCard = event.currentTarget.closest('.promo-card');
            if (!currentCard) return;

            const isActive = currentCard.classList.contains('active');

            console.log(`Toggling promo: ${currentCard.querySelector('.promo-card__title')?.textContent}. Currently active: ${isActive}`);

            // Close other cards if needed (optional)
            allPromoCards.forEach(otherCard => {
                if (otherCard !== currentCard) {
                    otherCard.classList.remove('active');
                    const otherToggle = otherCard.querySelector('.promo-card__toggle');
                    const otherContent = otherCard.querySelector('.promo-card__content');
                    if (otherToggle) {
                        otherToggle.textContent = 'Подробнее';
                    }
                    if (otherContent) {
                        otherContent.style.maxHeight = '0';
                    }
                }
            });

            // Toggle current card
            if (isActive) {
                currentCard.classList.remove('active');
                if (toggleButton) toggleButton.textContent = 'Подробнее';
                content.style.maxHeight = '0';
            } else {
                currentCard.classList.add('active');
                if (toggleButton) toggleButton.textContent = 'Свернуть';
                content.style.maxHeight = `${contentInner.scrollHeight}px`;
            }
        };

        // Set up event listeners
        if (header) {
            header.addEventListener('click', handleToggle);
            header.style.cursor = 'pointer';
        }

        if (toggleButton) {
            toggleButton.addEventListener('click', handleToggle);
            toggleButton.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleToggle(e);
                }
            });
        }

        // Handle resize events to adjust max-height
        let resizeTimer;
        window.addEventListener('resize', () => {
            if (card.classList.contains('active')) {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => {
                    content.style.maxHeight = `${contentInner.scrollHeight}px`;
                }, 100);
            }
        });
    });

    console.log("Promo Card Toggles Initialized.");
});