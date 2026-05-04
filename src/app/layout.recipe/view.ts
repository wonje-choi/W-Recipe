import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public user: any = null;
    public mobileOpen: boolean = false;
    public loginOpen: boolean = false;
    public loginTab: string = 'user';
    public loginLoading: boolean = false;
    public loginError: string = '';
    public currentLang: string = 'ko';
    public koLang: any = {};
    public lang: any = {};
    public loginForm: any = {
        email: '',
        password: '',
    };
    public loginEventHandler: any = null;

    public setCsrfToken(data: any) {
        if (data && data.csrfToken) {
            (window as any).recipeCsrfToken = data.csrfToken;
        }
    }

    public navItems: any[] = [
        { labelKey: 'nav.home', label: '메인페이지', href: '/' },
        { labelKey: 'nav.recipes', label: '레시피', href: '/recipes' },
        { labelKey: 'nav.lowSodium', label: '저염레시피', href: '/recipes/low-sodium' },
        { labelKey: 'nav.babyFood', label: '이유식레시피', href: '/recipes/baby-food' },
        { labelKey: 'nav.mypage', label: '마이페이지', href: '/mypage', auth: true },
        { labelKey: 'nav.admin', label: '관리자', href: '/dashboard', admin: true },
        { labelKey: 'nav.adminRecipes', label: '레시피 관리', href: '/admin/recipes', admin: true },
        { labelKey: 'nav.adminAi', label: 'AI 관리', href: '/admin/ai?tab=reviews', admin: true },
        { labelKey: 'nav.adminSettings', label: '설정', href: '/admin/ai?tab=settings', admin: true },
        { labelKey: 'nav.adminSources', label: '출처 관리', href: '/admin/sources', admin: true },
        { labelKey: 'nav.adminCollector', label: '수집 대시보드', href: '/admin/collector', admin: true },
        { labelKey: 'nav.adminFeedback', label: '참여 관리', href: '/admin/feedback', admin: true },
        { labelKey: 'nav.adminLogs', label: '시스템 로그', href: '/admin/logs', admin: true },
    ];

    public async ngOnInit() {
        await this.service.init();
        this.currentLang = this.detectLang();
        await this.loadLang(this.currentLang);
        this.loginEventHandler = async (event: any) => {
            let tab = event && event.detail && event.detail.tab ? event.detail.tab : 'user';
            await this.openLogin(tab);
        };
        window.addEventListener('recipe-open-login', this.loginEventHandler);
        await this.loadUser();
        await this.service.render();
    }

    public detectLang() {
        let params = new URLSearchParams(location.search);
        let lang = params.get('lang') || document.documentElement.lang || 'ko';
        return lang === 'en' ? 'en' : 'ko';
    }

    public async loadLang(lang: string) {
        this.currentLang = lang === 'en' ? 'en' : 'ko';
        document.documentElement.lang = this.currentLang;
        try {
            let ko = await fetch('/assets/lang/ko.json').then((response) => response.json());
            this.koLang = ko || {};
        } catch (error) {
            this.koLang = {};
        }
        try {
            let data = await fetch(`/assets/lang/${this.currentLang}.json`).then((response) => response.json());
            this.lang = data || {};
        } catch (error) {
            this.lang = {};
        }
    }

    public t(key: string, fallback: string = '') {
        return this.lang[key] || this.koLang[key] || fallback || key;
    }

    public label(item: any) {
        return this.t(item.labelKey, item.label);
    }

    public async switchLang(lang: string) {
        await this.loadLang(lang);
        let url = new URL(location.href);
        url.searchParams.set('lang', this.currentLang);
        history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
        await this.service.render();
    }

    public async loadUser() {
        let code = 500;
        let data: any = {};
        try {
            let response = await wiz.call('me');
            code = response.code;
            data = response.data || {};
        } catch (error) {
            this.user = null;
            return;
        }
        if (code === 200) {
            this.setCsrfToken(data);
            this.user = data.user || null;
        } else {
            this.user = null;
        }
    }

    public isAdmin() {
        return this.user && this.user.role === 'admin';
    }

    public isPremium() {
        if (this.isAdmin()) return true;
        if (!this.user || this.user.subscriptionPlan !== 'premium') return false;
        if (!this.user.subscriptionExpiresAt) return true;
        return new Date(this.user.subscriptionExpiresAt).getTime() >= Date.now();
    }

    public visibleItems() {
        return this.navItems.filter((item) => {
            if (item.admin) return this.isAdmin();
            if (item.premium) return this.isPremium();
            return !item.auth || this.user;
        });
    }

    public isActive(href: string) {
        let url = new URL(href, location.origin);
        if (url.pathname === '/') return location.pathname === '/';
        if (url.searchParams.has('tab')) {
            let current = new URL(location.href);
            return location.pathname === url.pathname && current.searchParams.get('tab') === url.searchParams.get('tab');
        }
        return location.pathname.indexOf(url.pathname) === 0;
    }

    public async toggleMobile() {
        this.mobileOpen = !this.mobileOpen;
        await this.service.render();
    }

    public async closeMobile() {
        this.mobileOpen = false;
        await this.service.render();
    }

    public async openLogin(tab: string = 'user') {
        this.loginTab = tab;
        this.loginOpen = true;
        this.loginError = '';
        await this.service.render();
    }

    public async closeLogin() {
        if (this.loginLoading) return;
        this.loginOpen = false;
        this.loginError = '';
        await this.service.render();
    }

    public async selectLoginTab(tab: string) {
        this.loginTab = tab;
        this.loginError = '';
        await this.service.render();
    }

    public async login() {
        if (this.loginLoading) return;
        this.loginError = '';
        if (!this.loginForm.email || !this.loginForm.password) {
            this.loginError = this.t('auth.missing', '이메일과 비밀번호를 입력해주세요.');
            await this.service.render();
            return;
        }
        this.loginLoading = true;
        await this.service.render();
        let code = 500;
        let data: any = {};
        try {
            let response = await wiz.call('login', {
                email: this.loginForm.email,
                password: this.loginForm.password,
            });
            code = response.code;
            data = response.data || {};
        } catch (error) {
            data = { message: this.t('auth.failed', '로그인에 실패했습니다.') };
        }
        this.loginLoading = false;
        this.setCsrfToken(data);
        if (code === 200) {
            this.user = data.user;
            this.loginOpen = false;
            this.loginError = '';
            this.loginForm.password = '';
            await this.service.render();
            return;
        }
        this.loginError = data.message || this.t('auth.failed', '로그인에 실패했습니다.');
        await this.service.render();
    }

    public async logout() {
        let data: any = {};
        try {
            let response = await wiz.call('logout', {});
            data = response.data || {};
        } catch (error) {
            data = {};
        }
        this.setCsrfToken(data);
        this.user = null;
        this.mobileOpen = false;
        await this.service.render();
        location.href = '/';
    }

    public go(href: string) {
        let url = new URL(href, location.origin);
        url.searchParams.set('lang', this.currentLang);
        location.href = `${url.pathname}${url.search}${url.hash}`;
    }
}
