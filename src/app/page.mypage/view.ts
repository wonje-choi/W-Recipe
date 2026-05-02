import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public savingProfile: boolean = false;
    public savingPreference: boolean = false;
    public message: string = '';
    public activeTab: string = 'activity';
    public profile: any = null;
    public preference: any = {};
    public activity: any = {
        favorites: { items: [], total: 0 },
        recentViews: { items: [], total: 0 },
        comments: { items: [], total: 0 },
        editRequests: { items: [], total: 0 },
        aiModifications: { items: [], total: 0 },
    };
    public options: any = {
        dietTypes: [],
        tools: [],
        sodiumPreferences: [],
        texturePreferences: [],
    };
    public preferenceText: any = {
        allergies: '',
        dislikedIngredients: '',
    };

    public tabs: any[] = [
        { label: '활동', value: 'activity' },
        { label: '개인화 설정', value: 'preference' },
        { label: '프로필', value: 'profile' },
    ];

    public async ngOnInit() {
        await this.service.init();
        await this.load();
    }

    public async load() {
        this.loading = true;
        await this.service.render();
        let { code, data } = await wiz.call('load', {});
        this.loading = false;
        if (code === 200) {
            this.profile = data.profile;
            this.preference = data.preference || {};
            this.activity = data.activity || this.activity;
            this.options = data.options || this.options;
            this.syncPreferenceText();
        } else {
            this.message = data.message || '마이페이지를 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public syncPreferenceText() {
        this.preferenceText.allergies = (this.preference.allergies || []).join(', ');
        this.preferenceText.dislikedIngredients = (this.preference.dislikedIngredients || []).join(', ');
    }

    public toList(text: string) {
        return (text || '').split(',').map((item) => item.trim()).filter((item) => !!item);
    }

    public async selectTab(tab: string) {
        this.activeTab = tab;
        this.message = '';
        await this.service.render();
    }

    public toggleArray(field: string, value: string) {
        let current = this.preference[field] || [];
        if (current.indexOf(value) >= 0) {
            this.preference[field] = current.filter((item: string) => item !== value);
        } else {
            this.preference[field] = current.concat([value]);
        }
    }

    public selected(field: string, value: string) {
        return (this.preference[field] || []).indexOf(value) >= 0;
    }

    public async saveProfile() {
        if (!this.profile || this.savingProfile) return;
        this.savingProfile = true;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('save_profile', { nickname: this.profile.nickname });
        this.savingProfile = false;
        if (code === 200) {
            this.profile = data.profile;
            this.message = '프로필이 저장되었습니다.';
        } else {
            this.message = data.message || '프로필 저장에 실패했습니다.';
        }
        await this.service.render();
    }

    public async savePreference() {
        if (this.savingPreference) return;
        this.savingPreference = true;
        this.message = '';
        let payload = Object.assign({}, this.preference, {
            allergies: this.toList(this.preferenceText.allergies),
            dislikedIngredients: this.toList(this.preferenceText.dislikedIngredients),
        });
        await this.service.render();
        let { code, data } = await wiz.call('save_preference', payload);
        this.savingPreference = false;
        if (code === 200) {
            this.preference = data.preference;
            this.syncPreferenceText();
            this.message = '개인화 설정이 저장되었습니다.';
        } else {
            this.message = data.message || '개인화 설정 저장에 실패했습니다.';
        }
        await this.service.render();
    }

    public openVersion(item: any) {
        let version = item && item.version;
        if (!version || !version.dishId) return;
        location.href = `/recipes/detail/${version.dishId}?version=${encodeURIComponent(version.id)}`;
    }

    public countOf(key: string) {
        return this.activity && this.activity[key] ? this.activity[key].total || 0 : 0;
    }

    public statusLabel(status: string) {
        let labels: any = {
            pending_review: '검수 대기',
            approved: '승인',
            rejected: '반려',
            open: '접수',
            in_review: '검토 중',
            resolved: '해결',
            visible: '표시 중',
            deleted: '삭제됨',
        };
        return labels[status] || status || '-';
    }

    public subscriptionLabel() {
        if (!this.profile) return 'Free';
        return this.profile.subscriptionPlan === 'premium' ? 'Premium' : 'Free';
    }

    public subscriptionExpiresAt() {
        if (!this.profile || !this.profile.subscriptionExpiresAt) return '기간 제한 없음';
        return this.profile.subscriptionExpiresAt;
    }
}
