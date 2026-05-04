import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public activeTab: string = 'reviews';
    public message: string = '';
    public options: any = {
        aiStatuses: [],
        logStatuses: [],
        purposes: [],
        promptTypes: [],
    };
    public settings: any = {
        autoApproveThreshold: 0.85,
        youtubeApiKey: '',
        youtubeApiKeyConfigured: false,
        youtubeApiKeyMasked: '',
    };
    public settingsMessage: string = '';

    public reviewLoading: boolean = false;
    public reviewItems: any[] = [];
    public selectedReview: any = null;
    public reviewReason: string = '';
    public reviewMessage: string = '';
    public reviewPage: number = 1;
    public reviewTotal: number = 0;
    public reviewFilters: any = {
        status: 'pending_review',
        purpose: '',
    };

    public promptLoading: boolean = false;
    public promptItems: any[] = [];
    public promptPage: number = 1;
    public promptTotal: number = 0;
    public promptFilters: any = {
        promptKey: '',
        isActive: '',
    };
    public promptForm: any = this.blankPrompt();
    public promptMessage: string = '';

    public logLoading: boolean = false;
    public logItems: any[] = [];
    public logPage: number = 1;
    public logTotal: number = 0;
    public logTokenTotal: number = 0;
    public logCostTotal: string = '0';
    public logFilters: any = {
        status: '',
        requestType: '',
    };

    public async ngOnInit() {
        await this.service.init();
        this.syncFromLocation();
        await this.loadOptions();
        await this.loadSettings();
        await this.loadActive();
        this.loading = false;
        await this.service.render();
    }

    public syncFromLocation() {
        let params = new URLSearchParams(location.search);
        this.activeTab = params.get('tab') || 'reviews';
        this.reviewFilters.status = params.get('status') || 'pending_review';
        this.logFilters.status = params.get('logStatus') || (this.activeTab === 'logs' ? params.get('status') || '' : '');
    }

    public updateUrl() {
        let params = new URLSearchParams();
        params.set('tab', this.activeTab);
        if (this.activeTab === 'reviews' && this.reviewFilters.status) params.set('status', this.reviewFilters.status);
        if (this.activeTab === 'logs' && this.logFilters.status) params.set('logStatus', this.logFilters.status);
        history.replaceState(null, '', `/admin/ai?${params.toString()}`);
    }

    public async loadOptions() {
        let { code, data } = await wiz.call('options', {});
        if (code === 200) {
            this.options = data;
        } else {
            this.message = data.message || 'AI 관리 옵션을 불러오지 못했습니다.';
        }
    }

    public async loadSettings() {
        let { code, data } = await wiz.call('get_settings', {});
        if (code === 200) {
            this.settings = data.settings || this.settings;
        } else {
            this.settingsMessage = data.message || 'AI 설정을 불러오지 못했습니다.';
        }
    }

    public async saveSettings() {
        this.settingsMessage = '';
        let { code, data } = await wiz.call('save_settings', {
            autoApproveThreshold: Number(this.settings.autoApproveThreshold || 0),
            youtubeApiKey: this.settings.youtubeApiKey || '',
        });
        if (code === 200) {
            this.settings = data.settings || this.settings;
            this.settings.youtubeApiKey = '';
            this.settingsMessage = '설정을 저장했습니다.';
            await this.loadReviews(this.reviewPage);
            return;
        }
        this.settingsMessage = data.message || 'AI 설정 저장에 실패했습니다.';
        await this.service.render();
    }

    public async setTab(tab: string) {
        this.activeTab = tab;
        this.message = '';
        this.updateUrl();
        await this.loadActive();
        await this.service.render();
    }

    public async loadActive() {
        if (this.activeTab === 'reviews') await this.loadReviews(1);
        if (this.activeTab === 'prompts') await this.loadPrompts(1);
        if (this.activeTab === 'logs') await this.loadLogs(1);
    }

    public async loadReviews(page: number = this.reviewPage) {
        this.reviewLoading = true;
        this.reviewMessage = '';
        this.reviewPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('reviews', {
            page: this.reviewPage,
            dump: 20,
            status: this.reviewFilters.status,
            purpose: this.reviewFilters.purpose,
        });
        this.reviewLoading = false;
        if (code === 200) {
            this.reviewItems = data.items || [];
            this.reviewTotal = data.total || 0;
            if (!this.selectedReview && this.reviewItems.length) this.selectedReview = this.reviewItems[0];
            if (this.selectedReview) {
                let matched = this.reviewItems.find((item: any) => item.id === this.selectedReview.id);
                if (matched) this.selectedReview = matched;
            }
        } else {
            this.reviewMessage = data.message || '검수 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async selectReview(item: any) {
        this.selectedReview = item;
        this.reviewReason = '';
        this.reviewMessage = '';
        await this.service.render();
    }

    public async reviewAction(action: string) {
        if (!this.selectedReview) return;
        if (action === 'reject' && !this.reviewReason.trim()) {
            this.reviewMessage = '반려 사유를 입력해주세요.';
            await this.service.render();
            return;
        }
        let label = action === 'approve' ? '승인' : '반려';
        if (!confirm(`선택한 AI 결과를 ${label}할까요?`)) return;
        this.reviewMessage = '';
        await this.service.render();
        let { code, data } = await wiz.call('review_action', {
            modificationId: this.selectedReview.id,
            action,
            reason: this.reviewReason,
        });
        if (code === 200) {
            this.selectedReview = data.item;
            this.reviewReason = '';
            this.reviewMessage = `${label} 처리했습니다.`;
            await this.loadReviews(this.reviewPage);
            return;
        }
        this.reviewMessage = data.message || `${label} 처리에 실패했습니다.`;
        await this.service.render();
    }

    public async regenerateReview() {
        if (!this.selectedReview) return;
        if (!confirm('선택한 AI 결과를 같은 조건으로 재생성할까요?')) return;
        this.reviewMessage = '';
        await this.service.render();
        let { code, data } = await wiz.call('regenerate', { modificationId: this.selectedReview.id });
        if (code === 201) {
            this.selectedReview = data.item;
            this.reviewMessage = '새 검수 대기 결과를 생성했습니다.';
            await this.loadReviews(1);
            return;
        }
        this.reviewMessage = data.message || '재생성에 실패했습니다.';
        await this.service.render();
    }

    public async loadPrompts(page: number = this.promptPage) {
        this.promptLoading = true;
        this.promptMessage = '';
        this.promptPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('prompts', {
            page: this.promptPage,
            dump: 20,
            promptKey: this.promptFilters.promptKey,
            isActive: this.promptFilters.isActive,
        });
        this.promptLoading = false;
        if (code === 200) {
            this.promptItems = data.items || [];
            this.promptTotal = data.total || 0;
            if (!this.promptForm.id && this.promptItems.length) this.editPrompt(this.promptItems[0]);
        } else {
            this.promptMessage = data.message || '프롬프트 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async newPrompt() {
        this.promptForm = this.blankPrompt();
        this.promptMessage = '';
        await this.service.render();
    }

    public async editPrompt(prompt: any) {
        this.promptForm = {
            id: prompt.id || '',
            promptKey: prompt.promptKey || 'taste_improvement',
            version: prompt.version || '',
            title: prompt.title || '',
            description: prompt.description || '',
            template: prompt.template || '',
            inputSchemaText: this.prettyJson(prompt.inputSchema || {}),
            outputSchemaText: this.prettyJson(prompt.outputSchema || {}),
            modelHint: prompt.modelHint || '',
            isActive: !!prompt.isActive,
            changeReason: prompt.changeReason || '',
        };
        this.promptMessage = '';
        await this.service.render();
    }

    public async savePrompt() {
        this.promptMessage = '';
        if (!this.promptForm.promptKey || !this.promptForm.version || !this.promptForm.template) {
            this.promptMessage = '프롬프트 유형, 버전, 템플릿은 필수입니다.';
            await this.service.render();
            return;
        }
        let { code, data } = await wiz.call('save_prompt', {
            id: this.promptForm.id,
            promptKey: this.promptForm.promptKey,
            version: this.promptForm.version,
            title: this.promptForm.title,
            description: this.promptForm.description,
            template: this.promptForm.template,
            inputSchema: this.promptForm.inputSchemaText,
            outputSchema: this.promptForm.outputSchemaText,
            modelHint: this.promptForm.modelHint,
            isActive: this.promptForm.isActive,
            changeReason: this.promptForm.changeReason,
        });
        if (code === 200) {
            this.promptMessage = '프롬프트를 저장했습니다.';
            await this.loadPrompts(this.promptPage);
            await this.editPrompt(data.prompt);
            return;
        }
        this.promptMessage = data.message || '프롬프트 저장에 실패했습니다.';
        await this.service.render();
    }

    public async promptAction(action: string, prompt: any = this.promptForm) {
        if (!prompt || !prompt.id) return;
        let label = action === 'activate' ? '활성화' : '비활성화';
        if (!confirm(`프롬프트를 ${label}할까요?`)) return;
        let { code, data } = await wiz.call('prompt_action', {
            promptId: prompt.id,
            action,
            reason: this.promptForm.changeReason,
        });
        if (code === 200) {
            this.promptMessage = `프롬프트를 ${label}했습니다.`;
            await this.loadPrompts(this.promptPage);
            await this.editPrompt(data.prompt);
            return;
        }
        this.promptMessage = data.message || `프롬프트 ${label}에 실패했습니다.`;
        await this.service.render();
    }

    public async loadLogs(page: number = this.logPage) {
        this.logLoading = true;
        this.logPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('logs', {
            page: this.logPage,
            dump: 20,
            status: this.logFilters.status,
            requestType: this.logFilters.requestType,
        });
        this.logLoading = false;
        if (code === 200) {
            this.logItems = data.items || [];
            this.logTotal = data.total || 0;
            this.logTokenTotal = data.tokenTotal || 0;
            this.logCostTotal = data.costTotal || '0';
        } else {
            this.message = data.message || 'AI 로그를 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public blankPrompt() {
        return {
            id: '',
            promptKey: 'taste_improvement',
            version: '',
            title: '',
            description: '',
            template: '',
            inputSchemaText: '{}',
            outputSchemaText: '{}',
            modelHint: '',
            isActive: false,
            changeReason: '',
        };
    }

    public prettyJson(value: any) {
        try {
            return JSON.stringify(value || {}, null, 2);
        } catch (error) {
            return '{}';
        }
    }

    public statusClass(status: string) {
        if (status === 'approved' || status === 'completed') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
        if (status === 'pending_review' || status === 'processing' || status === 'queued') return 'bg-amber-50 text-amber-700 border-amber-200';
        if (status === 'failed' || status === 'rejected') return 'bg-rose-50 text-rose-700 border-rose-200';
        return 'bg-zinc-50 text-zinc-600 border-zinc-200';
    }

    public riskClass(severity: string) {
        if (severity === 'danger') return 'bg-rose-50 text-rose-700 border-rose-200';
        if (severity === 'warning') return 'bg-amber-50 text-amber-700 border-amber-200';
        return 'bg-zinc-50 text-zinc-600 border-zinc-200';
    }

    public totalPages(total: number) {
        return Math.max(1, Math.ceil((total || 0) / 20));
    }

    public async previous(kind: string) {
        if (kind === 'reviews' && this.reviewPage > 1) await this.loadReviews(this.reviewPage - 1);
        if (kind === 'prompts' && this.promptPage > 1) await this.loadPrompts(this.promptPage - 1);
        if (kind === 'logs' && this.logPage > 1) await this.loadLogs(this.logPage - 1);
    }

    public async next(kind: string) {
        if (kind === 'reviews' && this.reviewPage < this.totalPages(this.reviewTotal)) await this.loadReviews(this.reviewPage + 1);
        if (kind === 'prompts' && this.promptPage < this.totalPages(this.promptTotal)) await this.loadPrompts(this.promptPage + 1);
        if (kind === 'logs' && this.logPage < this.totalPages(this.logTotal)) await this.loadLogs(this.logPage + 1);
    }
}
