import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public saving: boolean = false;
    public message: string = '';
    public items: any[] = [];
    public total: number = 0;
    public page: number = 1;
    public dump: number = 12;
    public statusSummary: any[] = [];
    public retrySummary: any = { failed: 0, retryable: 0 };
    public selectedSource: any = null;
    public formOpen: boolean = false;
    public batchOpen: boolean = false;
    public batchUrls: string = '';
    public batchImporting: boolean = false;
    public batchResult: any = null;
    public formMessage: string = '';
    public actionLoadingId: string = '';

    public options: any = {
        sourceTypes: [],
        crawlStatuses: [],
    };

    public filters: any = {
        text: '',
        status: '',
        sourceType: '',
    };

    public form: any = this.blankForm();

    public async ngOnInit() {
        await this.service.init();
        this.syncFromLocation();
        await this.loadOptions();
        await this.load();
    }

    public syncFromLocation() {
        let params = new URLSearchParams(location.search);
        this.filters.text = params.get('text') || '';
        this.filters.status = params.get('status') || '';
        this.filters.sourceType = params.get('sourceType') || '';
        this.page = Number(params.get('page') || 1);
    }

    public updateUrl() {
        let params = new URLSearchParams();
        if (this.filters.text) params.set('text', this.filters.text);
        if (this.filters.status) params.set('status', this.filters.status);
        if (this.filters.sourceType) params.set('sourceType', this.filters.sourceType);
        if (this.page > 1) params.set('page', String(this.page));
        let query = params.toString();
        history.replaceState(null, '', query ? `/admin/sources?${query}` : '/admin/sources');
    }

    public async loadOptions() {
        let { code, data } = await wiz.call('options', {});
        if (code === 200) {
            this.options = data;
        } else {
            this.message = data.message || '출처 옵션을 불러오지 못했습니다.';
        }
    }

    public async load(page: number = this.page) {
        this.loading = true;
        this.message = '';
        this.page = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('sources', {
            page: this.page,
            dump: this.dump,
            text: this.filters.text,
            status: this.filters.status,
            sourceType: this.filters.sourceType,
        });
        this.loading = false;
        if (code === 200) {
            this.items = data.items || [];
            this.total = data.total || 0;
            this.statusSummary = data.statusSummary || [];
            this.retrySummary = data.retrySummary || { failed: 0, retryable: 0 };
            if (!this.selectedSource && this.items.length) this.selectSource(this.items[0], false);
            if (this.selectedSource) {
                let matched = this.items.find((item: any) => item.id === this.selectedSource.id);
                if (matched) this.selectSource(matched, false);
            }
        } else {
            this.message = data.message || '출처 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async search() {
        await this.load(1);
    }

    public async resetFilters() {
        this.filters = { text: '', status: '', sourceType: '' };
        await this.load(1);
    }

    public get totalPages() {
        return Math.max(1, Math.ceil(this.total / this.dump));
    }

    public async prevPage() {
        if (this.page <= 1) return;
        await this.load(this.page - 1);
    }

    public async nextPage() {
        if (this.page >= this.totalPages) return;
        await this.load(this.page + 1);
    }

    public async newSource() {
        this.selectedSource = null;
        this.form = this.blankForm();
        this.formOpen = true;
        this.batchOpen = false;
        this.formMessage = '';
        await this.service.render();
    }

    public async openBatch() {
        this.batchOpen = true;
        this.formOpen = false;
        this.batchResult = null;
        await this.service.render();
    }

    public selectSource(item: any, open: boolean = true) {
        this.selectedSource = item;
        this.form = this.sourceToForm(item);
        this.formOpen = open;
        if (open) this.batchOpen = false;
        this.formMessage = '';
    }

    public async openSource(item: any) {
        this.selectSource(item, true);
        await this.service.render();
    }

    public async closeForm() {
        this.formOpen = false;
        this.formMessage = '';
        await this.service.render();
    }

    public async closeBatch() {
        this.batchOpen = false;
        this.batchResult = null;
        await this.service.render();
    }

    public blankForm() {
        return {
            id: '',
            sourceUrl: '',
            sourceType: 'web',
            title: '',
            author: '',
            thumbnailUrl: '',
            collectedTextSummary: '',
            rawContent: '',
            crawlStatus: 'pending',
            robotsAllowed: false,
            errorMessage: '',
        };
    }

    public sourceToForm(source: any) {
        if (!source) return this.blankForm();
        return {
            id: source.id || '',
            sourceUrl: source.sourceUrl || '',
            sourceType: source.sourceType || 'web',
            title: source.title || '',
            author: source.author || '',
            thumbnailUrl: source.thumbnailUrl || '',
            collectedTextSummary: source.collectedTextSummary || '',
            rawContent: source.rawContent || '',
            crawlStatus: source.crawlStatus || 'pending',
            robotsAllowed: !!source.robotsAllowed,
            errorMessage: source.errorMessage || '',
        };
    }

    public async save() {
        if (this.saving) return;
        this.formMessage = '';
        if (!this.form.sourceUrl.trim()) {
            this.formMessage = '원본 URL을 입력해주세요.';
            await this.service.render();
            return;
        }
        this.saving = true;
        await this.service.render();
        let { code, data } = await wiz.call('save_source', this.form);
        this.saving = false;
        if (code === 200 || code === 201) {
            this.formMessage = data.source && data.source.duplicate ? '이미 등록된 URL입니다. 기존 항목을 열었습니다.' : '저장했습니다.';
            if (data.source) this.selectSource(data.source, true);
            await this.load(this.page);
            return;
        }
        this.formMessage = data.message || '출처 저장에 실패했습니다.';
        await this.service.render();
    }

    public async batchImport() {
        if (this.batchImporting) return;
        let text = (this.batchUrls || '').trim();
        if (!text) {
            this.batchResult = { message: '등록할 URL을 입력해주세요.' };
            await this.service.render();
            return;
        }
        this.batchImporting = true;
        this.batchResult = null;
        await this.service.render();
        let { code, data } = await wiz.call('batch_import', { urls: text });
        this.batchImporting = false;
        if (code === 200) {
            this.batchResult = data;
            await this.load(1);
            return;
        }
        this.batchResult = { message: data.message || '배치 등록에 실패했습니다.' };
        await this.service.render();
    }

    public async updateStatus(status: string) {
        if (!this.form.id) return;
        this.form.crawlStatus = status;
        if (status === 'allowed' || status === 'collected' || status === 'summarized') {
            this.form.robotsAllowed = true;
        }
        await this.submitStatus();
    }

    public async submitStatus() {
        if (!this.form.id) return;
        this.actionLoadingId = this.form.id;
        this.formMessage = '';
        await this.service.render();
        let { code, data } = await wiz.call('status_action', {
            id: this.form.id,
            crawlStatus: this.form.crawlStatus,
            robotsAllowed: this.form.robotsAllowed,
            errorMessage: this.form.errorMessage,
        });
        this.actionLoadingId = '';
        if (code === 200) {
            this.formMessage = '상태를 업데이트했습니다.';
            if (data.source) this.selectSource(data.source, true);
            await this.load(this.page);
            return;
        }
        this.formMessage = data.message || '상태 변경에 실패했습니다.';
        await this.service.render();
    }

    public async retrySource(item: any = this.selectedSource) {
        if (!item || !item.id) return;
        this.actionLoadingId = item.id;
        this.formMessage = '';
        await this.service.render();
        let { code, data } = await wiz.call('retry_source', { id: item.id });
        this.actionLoadingId = '';
        if (code === 200) {
            if (data.source) this.selectSource(data.source, this.formOpen);
            await this.load(this.page);
            return;
        }
        this.formMessage = data.message || '재시도 상태 변경에 실패했습니다.';
        await this.service.render();
    }

    public async retryFailed() {
        if (this.actionLoadingId) return;
        if (!confirm('재시도 가능한 실패 출처를 대기 상태로 전환할까요?')) return;
        this.actionLoadingId = 'retry_failed';
        this.formMessage = '';
        await this.service.render();
        let { code, data } = await wiz.call('retry_failed', {});
        this.actionLoadingId = '';
        if (code === 200) {
            this.retrySummary = data.retrySummary || this.retrySummary;
            await this.load(this.page);
            return;
        }
        this.message = data.message || '실패 출처 재시도 처리에 실패했습니다.';
        await this.service.render();
    }

    public async expireSource(item: any = this.selectedSource) {
        if (!item || !item.id) return;
        if (!confirm('이 링크를 만료 처리할까요?')) return;
        this.actionLoadingId = item.id;
        await this.service.render();
        let { code, data } = await wiz.call('expire_source', { id: item.id });
        this.actionLoadingId = '';
        if (code === 200) {
            if (data.source) this.selectSource(data.source, this.formOpen);
            await this.load(this.page);
            return;
        }
        this.formMessage = data.message || '만료 처리에 실패했습니다.';
        await this.service.render();
    }

    public openOriginal(item: any = this.selectedSource) {
        if (!item || !item.sourceUrl) return;
        window.open(item.sourceUrl, '_blank', 'noopener');
    }

    public statusLabel(status: string) {
        let item = (this.options.crawlStatuses || []).find((option: any) => option.value === status);
        return item ? item.label : status;
    }

    public sourceTypeLabel(sourceType: string) {
        let item = (this.options.sourceTypes || []).find((option: any) => option.value === sourceType);
        return item ? item.label : sourceType;
    }

    public statusClass(status: string) {
        if (status === 'allowed' || status === 'collected' || status === 'summarized') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
        if (status === 'failed' || status === 'blocked') return 'border-rose-200 bg-rose-50 text-rose-700';
        if (status === 'expired') return 'border-zinc-200 bg-zinc-100 text-zinc-500';
        return 'border-amber-200 bg-amber-50 text-amber-700';
    }

    public flagClass(flag: any) {
        if (!flag || !flag.active) return 'border-zinc-200 bg-zinc-50 text-zinc-500';
        if (flag.tone === 'emerald') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
        if (flag.tone === 'amber') return 'border-amber-200 bg-amber-50 text-amber-700';
        if (flag.tone === 'sky') return 'border-sky-200 bg-sky-50 text-sky-700';
        if (flag.tone === 'violet') return 'border-violet-200 bg-violet-50 text-violet-700';
        if (flag.tone === 'rose') return 'border-rose-200 bg-rose-50 text-rose-700';
        return 'border-zinc-200 bg-zinc-50 text-zinc-700';
    }

    public canRetry(item: any) {
        return item && (item.crawlStatus === 'failed' || item.crawlStatus === 'blocked' || item.linkExpired);
    }
}
