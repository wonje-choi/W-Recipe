import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public requestLoading: boolean = false;
    public resultLoading: boolean = false;
    public saving: boolean = false;
    public promoting: boolean = false;
    public actionLoadingId: string = '';
    public message: string = '';
    public formMessage: string = '';
    public promoteMessage: string = '';
    public options: any = { targetTypes: [], requestStatuses: [], resultStatuses: [], limits: { maxItems: 50, defaultItems: 10 }, settings: {} };
    public collectorPrompt: string = '';
    public improvementNotes: string[] = [];
    public requests: any[] = [];
    public results: any[] = [];
    public statusSummary: any[] = [];
    public requestTotal: number = 0;
    public resultTotal: number = 0;
    public requestPage: number = 1;
    public resultPage: number = 1;
    public requestDump: number = 8;
    public resultDump: number = 12;
    public selectedRequest: any = null;
    public selectedIds: any = {};

    public form: any = this.blankForm();
    public requestFilters: any = { text: '', status: '' };
    public resultFilters: any = { text: '', resultType: '', requestId: '' };

    public async ngOnInit() {
        await this.service.init();
        await this.loadDashboard();
    }

    public blankForm() {
        return {
            targetType: 'web_keyword',
            targetValue: '',
            maxItems: 10,
            includeComments: false,
            immediate: true,
        };
    }

    public async loadDashboard() {
        this.loading = true;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('dashboard', {});
        this.loading = false;
        if (code === 200) {
            this.options = data.options || this.options;
            this.collectorPrompt = this.options.collectorPrompt || '';
            this.improvementNotes = this.options.improvementNotes || [];
            this.requests = data.requests || [];
            this.results = data.results || [];
            this.requestTotal = data.requestTotal || 0;
            this.resultTotal = data.resultTotal || 0;
            this.statusSummary = data.statusSummary || [];
            if (!this.selectedRequest && this.requests.length) this.selectedRequest = this.requests[0];
        } else {
            this.message = data.message || '수집 대시보드를 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async submitRequest() {
        if (this.saving) return;
        this.formMessage = '';
        if (!String(this.form.targetValue || '').trim()) {
            this.formMessage = '수집 대상 값을 입력해주세요.';
            await this.service.render();
            return;
        }
        this.saving = true;
        await this.service.render();
        let { code, data } = await wiz.call('create_request', this.form);
        this.saving = false;
        if (code === 201 || code === 200) {
            this.formMessage = '수집 요청을 생성했습니다.';
            this.form = this.blankForm();
            if (data.request) this.selectedRequest = data.request;
            await this.loadRequests(1);
            await this.loadResults(1);
            return;
        }
        this.formMessage = data.message || '수집 요청 생성에 실패했습니다.';
        await this.service.render();
    }

    public async resetForm() {
        this.form = this.blankForm();
        this.formMessage = '';
        await this.service.render();
    }

    public async useKeywordMode(type: string) {
        this.form.targetType = type === 'youtube' ? 'youtube_keyword' : 'web_keyword';
        if (!this.form.targetValue) this.form.targetValue = '김치찌개';
        this.formMessage = type === 'youtube' ? '유튜브 키워드 수집 모드입니다.' : '웹 키워드 수집 모드입니다.';
        await this.service.render();
    }

    public promptForCurrentKeyword() {
        let keyword = String(this.form.targetValue || '').trim() || '레시피 키워드';
        let source = this.form.targetType.indexOf('youtube') === 0 ? 'YouTube 영상/채널' : '웹 문서/검색 결과';
        return [
            `키워드: ${keyword}`,
            `수집 대상: ${source}`,
            '',
            this.collectorPrompt || '원문 링크를 유지하고 재료, 조리 단계, 요약, 주의사항을 JSON으로 정리한다.',
        ].join('\n');
    }

    public async loadRequests(page: number = this.requestPage) {
        this.requestLoading = true;
        this.requestPage = page;
        await this.service.render();
        let { code, data } = await wiz.call('requests', {
            page: this.requestPage,
            dump: this.requestDump,
            status: this.requestFilters.status,
            text: this.requestFilters.text,
        });
        this.requestLoading = false;
        if (code === 200) {
            this.requests = data.items || [];
            this.requestTotal = data.total || 0;
            this.statusSummary = data.statusSummary || [];
        } else {
            this.message = data.message || '수집 기록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async loadResults(page: number = this.resultPage) {
        this.resultLoading = true;
        this.resultPage = page;
        await this.service.render();
        let { code, data } = await wiz.call('results', {
            page: this.resultPage,
            dump: this.resultDump,
            requestId: this.resultFilters.requestId,
            resultType: this.resultFilters.resultType,
            text: this.resultFilters.text,
        });
        this.resultLoading = false;
        if (code === 200) {
            this.results = data.items || [];
            this.resultTotal = data.total || 0;
            this.selectedIds = {};
        } else {
            this.message = data.message || '수집 결과를 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async selectRequest(item: any) {
        this.selectedRequest = item;
        this.resultFilters.requestId = item ? item.id : '';
        await this.loadResults(1);
    }

    public async clearRequestFilter() {
        this.selectedRequest = null;
        this.resultFilters.requestId = '';
        await this.loadResults(1);
    }

    public async retryRequest(item: any = this.selectedRequest) {
        if (!item || this.actionLoadingId) return;
        this.actionLoadingId = item.id;
        await this.service.render();
        let { code, data } = await wiz.call('retry_request', { id: item.id });
        this.actionLoadingId = '';
        if (code === 200) {
            this.selectedRequest = data.request || item;
            await this.loadRequests(this.requestPage);
            await this.loadResults(1);
            return;
        }
        this.message = data.message || '재시도에 실패했습니다.';
        await this.service.render();
    }

    public async deleteRequest(item: any) {
        if (!item || this.actionLoadingId) return;
        this.actionLoadingId = item.id;
        await this.service.render();
        let { code, data } = await wiz.call('delete_request', { id: item.id });
        this.actionLoadingId = '';
        if (code === 200) {
            if (this.selectedRequest && this.selectedRequest.id === item.id) this.selectedRequest = null;
            await this.loadRequests(this.requestPage);
            await this.loadResults(1);
            return;
        }
        this.message = data.message || '수집 요청 삭제에 실패했습니다.';
        await this.service.render();
    }

    public selectedResultIds() {
        return Object.keys(this.selectedIds).filter((id) => this.selectedIds[id]);
    }

    public selectedPromotableResultIds() {
        let promoted: any = {};
        for (let item of this.results || []) {
            if (item.promotedRecipeVersionId) promoted[item.id] = true;
        }
        return this.selectedResultIds().filter((id) => !promoted[id]);
    }

    public async promoteSelectedResults() {
        let ids = this.selectedPromotableResultIds();
        if (!ids.length || this.promoting) return;
        this.promoting = true;
        this.promoteMessage = '';
        await this.service.render();
        let { code, data } = await wiz.call('promote_results', { ids });
        this.promoting = false;
        if (code === 200) {
            this.promoteMessage = `검수 대기 등록 ${data.created || 0}건, 중복/스킵 ${data.skipped || 0}건, 실패 ${data.failed || 0}건`;
            await this.loadResults(this.resultPage);
            return;
        }
        this.promoteMessage = data.message || '레시피화에 실패했습니다.';
        await this.service.render();
    }

    public async deleteSelectedResults() {
        let ids = this.selectedResultIds();
        if (!ids.length) return;
        this.actionLoadingId = 'delete-results';
        await this.service.render();
        let { code, data } = await wiz.call('delete_results', { ids });
        this.actionLoadingId = '';
        if (code === 200) {
            await this.loadResults(this.resultPage);
            return;
        }
        this.message = data.message || '선택 결과 삭제에 실패했습니다.';
        await this.service.render();
    }

    public async exportResults(format: string) {
        this.actionLoadingId = `export-${format}`;
        await this.service.render();
        let ids = this.selectedResultIds();
        let { code, data } = await wiz.call('export_data', {
            format,
            ids,
            resultType: this.resultFilters.resultType,
            text: this.resultFilters.text,
        });
        this.actionLoadingId = '';
        if (code === 200) {
            this.download(data.filename, data.mime, data.content || '');
            await this.service.render();
            return;
        }
        this.message = data.message || '내보내기에 실패했습니다.';
        await this.service.render();
    }

    public download(filename: string, mime: string, content: string) {
        let blob = new Blob([content], { type: mime || 'text/plain;charset=utf-8' });
        let url = URL.createObjectURL(blob);
        let link = document.createElement('a');
        link.href = url;
        link.download = filename || 'collector-results.txt';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    public openOriginal(item: any) {
        if (!item || !item.url) return;
        window.open(item.url, '_blank', 'noopener,noreferrer');
    }

    public hasRecipeDetail(item: any) {
        return (item.ingredients && item.ingredients.length) || (item.steps && item.steps.length) || (item.sourceLinks && item.sourceLinks.length);
    }

    public statusClass(status: string) {
        if (status === 'done' || status === 'stored') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
        if (status === 'running' || status === 'queued') return 'border-sky-200 bg-sky-50 text-sky-700';
        if (status === 'failed') return 'border-rose-200 bg-rose-50 text-rose-700';
        return 'border-zinc-200 bg-zinc-50 text-zinc-600';
    }

    public targetLabel(value: string) {
        let matched = (this.options.targetTypes || []).find((item: any) => item.value === value);
        return matched ? matched.label : value;
    }

    public get requestTotalPages() {
        return Math.max(1, Math.ceil(this.requestTotal / this.requestDump));
    }

    public get resultTotalPages() {
        return Math.max(1, Math.ceil(this.resultTotal / this.resultDump));
    }
}
