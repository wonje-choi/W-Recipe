import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

declare const wiz: any;

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public message: string = '';
    public items: any[] = [];
    public selected: any = null;
    public page: number = 1;
    public dump: number = 20;
    public total: number = 0;

    public options: any = {
        logTypes: [],
        severities: [],
    };

    public summary: any = {
        admin_action: 0,
        login_failure: 0,
        ai_failure: 0,
        crawling_failure: 0,
        api_error: 0,
        permission_error: 0,
    };

    public filters: any = {
        type: '',
        severity: '',
        adminUserId: '',
        targetType: '',
        fromDate: '',
        toDate: '',
        text: '',
    };

    public async ngOnInit() {
        await this.service.init();
        this.syncFromLocation();
        await this.loadOptions();
        await this.load();
    }

    public syncFromLocation() {
        let params = new URLSearchParams(location.search);
        this.filters.type = params.get('type') || '';
        this.filters.severity = params.get('severity') || '';
        this.filters.adminUserId = params.get('adminUserId') || '';
        this.filters.targetType = params.get('targetType') || '';
        this.filters.fromDate = params.get('fromDate') || '';
        this.filters.toDate = params.get('toDate') || '';
        this.filters.text = params.get('text') || '';
        this.page = Number(params.get('page') || 1);
    }

    public updateUrl() {
        let params = new URLSearchParams();
        if (this.filters.type) params.set('type', this.filters.type);
        if (this.filters.severity) params.set('severity', this.filters.severity);
        if (this.filters.adminUserId) params.set('adminUserId', this.filters.adminUserId);
        if (this.filters.targetType) params.set('targetType', this.filters.targetType);
        if (this.filters.fromDate) params.set('fromDate', this.filters.fromDate);
        if (this.filters.toDate) params.set('toDate', this.filters.toDate);
        if (this.filters.text) params.set('text', this.filters.text);
        if (this.page > 1) params.set('page', String(this.page));
        let query = params.toString();
        history.replaceState(null, '', query ? `/admin/logs?${query}` : '/admin/logs');
    }

    public async loadOptions() {
        let { code, data } = await wiz.call('options', {});
        if (code === 200) {
            this.options = data;
        } else {
            this.message = data.message || '로그 옵션을 불러오지 못했습니다.';
        }
    }

    public async load(page: number = this.page) {
        this.loading = true;
        this.message = '';
        this.page = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('logs', {
            page: this.page,
            dump: this.dump,
            type: this.filters.type,
            severity: this.filters.severity,
            adminUserId: this.filters.adminUserId,
            targetType: this.filters.targetType,
            fromDate: this.filters.fromDate,
            toDate: this.filters.toDate,
            text: this.filters.text,
        });
        this.loading = false;
        if (code === 200) {
            this.items = data.items || [];
            this.total = data.total || 0;
            this.summary = data.summary || this.summary;
            this.refreshSelection();
        } else {
            this.message = data.message || '시스템 로그를 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public refreshSelection() {
        if (this.selected) {
            let matched = this.items.find((item: any) => item.id === this.selected.id && item.type === this.selected.type);
            if (matched) {
                this.selected = matched;
                return;
            }
        }
        this.selected = this.items.length ? this.items[0] : null;
    }

    public async search() {
        await this.load(1);
    }

    public async resetFilters() {
        this.filters = {
            type: '',
            severity: '',
            adminUserId: '',
            targetType: '',
            fromDate: '',
            toDate: '',
            text: '',
        };
        await this.load(1);
    }

    public async quickType(type: string) {
        this.filters.type = type;
        await this.load(1);
    }

    public async selectItem(item: any) {
        this.selected = item;
        await this.service.render();
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

    public typeLabel(type: string) {
        let item = (this.options.logTypes || []).find((option: any) => option.value === type);
        return item ? item.label : type;
    }

    public severityClass(severity: string) {
        if (severity === 'error') return 'border-rose-200 bg-rose-50 text-rose-700';
        if (severity === 'security') return 'border-violet-200 bg-violet-50 text-violet-700';
        if (severity === 'warning') return 'border-amber-200 bg-amber-50 text-amber-700';
        return 'border-sky-200 bg-sky-50 text-sky-700';
    }

    public typeClass(type: string) {
        if (type === 'admin_action') return 'border-zinc-200 bg-zinc-50 text-zinc-700';
        if (type === 'login_failure' || type === 'permission_error') return 'border-violet-200 bg-violet-50 text-violet-700';
        if (type === 'ai_failure' || type === 'api_error') return 'border-rose-200 bg-rose-50 text-rose-700';
        if (type === 'crawling_failure') return 'border-amber-200 bg-amber-50 text-amber-700';
        return 'border-zinc-200 bg-white text-zinc-600';
    }

    public summaryCount(type: string) {
        return this.summary[type] || 0;
    }
}
