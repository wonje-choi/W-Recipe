import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public commentsLoading: boolean = false;
    public submittingComment: boolean = false;
    public submittingEditRequest: boolean = false;
    public dishId: string = '';
    public errorMessage: string = '';
    public dish: any = null;
    public versions: any[] = [];
    public selectedVersion: any = null;
    public source: any = null;
    public comparison: any = null;
    public user: any = null;
    public comments: any[] = [];
    public commentsTotal: number = 0;
    public commentText: string = '';
    public commentMessage: string = '';
    public editOpen: boolean = false;
    public sourceRawOpen: boolean = false;
    public editMessage: string = '';
    public editForm: any = {
        requestType: 'error',
        content: '',
        attachmentUrl: '',
    };

    public editRequestOptions: any[] = [
        { label: '정보 오류', value: 'error' },
        { label: '계량 문제', value: 'measurement_issue' },
        { label: '출처 문제', value: 'source_issue' },
        { label: '맛 개선 제안', value: 'taste_improvement' },
        { label: '기타', value: 'other' },
    ];

    public fallbackImage: string = 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=1200&q=80';

    public async ngOnInit() {
        await this.service.init();
        this.syncFromLocation();
        await this.load();
    }

    public syncFromLocation() {
        let parts = location.pathname.split('/').filter((item) => item);
        this.dishId = parts[2] || '';
    }

    public currentVersionQuery() {
        let params = new URLSearchParams(location.search);
        return params.get('version') || '';
    }

    public async load() {
        this.loading = true;
        this.errorMessage = '';
        await this.service.render();
        let { code, data } = await wiz.call('load', {
            dishId: this.dishId,
            versionId: this.currentVersionQuery(),
        });
        this.loading = false;
        if (code === 200) {
            this.dish = data.dish;
            this.versions = data.versions || [];
            this.selectedVersion = data.selectedVersion;
            this.source = data.source;
            this.comparison = data.comparison;
            this.user = data.user;
            await this.loadComments();
        } else {
            this.errorMessage = data.message || '레시피를 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async loadComments() {
        if (!this.selectedVersion || !this.selectedVersion.id) return;
        this.commentsLoading = true;
        await this.service.render();
        let { code, data } = await wiz.call('comments', {
            versionId: this.selectedVersion.id,
            page: 1,
            dump: 30,
        });
        this.commentsLoading = false;
        if (code === 200) {
            this.comments = data.comments || [];
            this.commentsTotal = data.total || 0;
        }
        await this.service.render();
    }

    public selectVersion(version: any) {
        if (!version || !version.id) return;
        location.href = `/recipes/detail/${this.dishId}?version=${encodeURIComponent(version.id)}`;
    }

    public goList() {
        location.href = '/recipes';
    }

    public imageStyle() {
        let image = (this.dish && this.dish.thumbnailUrl) || this.fallbackImage;
        if (image === this.fallbackImage) return `url('${this.fallbackImage}')`;
        return `url('${image}'), url('${this.fallbackImage}')`;
    }

    public asList(value: any) {
        if (!value) return [];
        if (Array.isArray(value)) return value;
        if (typeof value === 'string') return value ? [value] : [];
        return Object.keys(value).map((key) => ({ key, value: value[key] }));
    }

    public objectEntries(value: any) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) return [];
        return Object.keys(value).map((key) => ({ key, value: value[key] }));
    }

    public itemText(item: any) {
        if (item === null || item === undefined) return '';
        if (typeof item === 'string' || typeof item === 'number') return String(item);
        if (item.name && item.amount) return `${item.name} ${item.amount}`;
        if (item.ingredient && item.amount) return `${item.ingredient} ${item.amount}`;
        if (item.title && item.content) return `${item.title}: ${item.content}`;
        if (item.key !== undefined && item.value !== undefined) return `${item.key}: ${item.value}`;
        return JSON.stringify(item);
    }

    public sourceTitle() {
        if (!this.source) return '';
        return this.source.sourceTitle || this.source.sourceUrl || this.source.message || '';
    }

    public hasSourceRawContent() {
        return !!(this.source && this.source.rawContentStoragePolicy === 'full' && this.source.rawContent);
    }

    public async toggleSourceRaw() {
        this.sourceRawOpen = !this.sourceRawOpen;
        await this.service.render();
    }

    public changed(flag: string) {
        return this.comparison && this.comparison.comparison && this.comparison.comparison[flag];
    }

    public async submitComment() {
        if (!this.selectedVersion || this.submittingComment) return;
        this.commentMessage = '';
        let content = (this.commentText || '').trim();
        if (!content) {
            this.commentMessage = '댓글 내용을 입력해주세요.';
            await this.service.render();
            return;
        }
        this.submittingComment = true;
        await this.service.render();
        let { code, data } = await wiz.call('create_comment', {
            versionId: this.selectedVersion.id,
            content,
        });
        this.submittingComment = false;
        if (code === 201) {
            this.commentText = '';
            this.commentMessage = '';
            await this.loadComments();
            return;
        }
        this.commentMessage = data.message || '댓글을 등록하지 못했습니다.';
        await this.service.render();
    }

    public async toggleEditRequest() {
        this.editOpen = !this.editOpen;
        this.editMessage = '';
        await this.service.render();
    }

    public async submitEditRequest() {
        if (!this.selectedVersion || this.submittingEditRequest) return;
        this.editMessage = '';
        let content = (this.editForm.content || '').trim();
        if (!content) {
            this.editMessage = '수정 요청 내용을 입력해주세요.';
            await this.service.render();
            return;
        }
        this.submittingEditRequest = true;
        await this.service.render();
        let { code, data } = await wiz.call('create_edit_request', {
            versionId: this.selectedVersion.id,
            requestType: this.editForm.requestType,
            content,
            attachmentUrl: this.editForm.attachmentUrl,
        });
        this.submittingEditRequest = false;
        if (code === 201) {
            this.editForm.content = '';
            this.editForm.attachmentUrl = '';
            this.editMessage = '수정 요청이 접수되었습니다.';
            await this.service.render();
            return;
        }
        this.editMessage = data.message || '수정 요청을 등록하지 못했습니다.';
        await this.service.render();
    }
}
