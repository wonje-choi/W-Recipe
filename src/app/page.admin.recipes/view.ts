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
    public filters: any = {
        text: '',
        status: '',
        category: '',
        tag: '',
        sort: 'latest',
    };

    public options: any = {
        recipeStatuses: [],
        sourceTypes: [],
        difficultyOptions: [],
        categories: [],
        tags: [],
    };

    public formOpen: boolean = false;
    public dishForm: any = this.blankDish();
    public versionForm: any = this.blankVersion();
    public versions: any[] = [];
    public selectedVersionId: string = '';
    public formMessage: string = '';
    public generatingMeta: boolean = false;
    public generatedMeta: any = null;
    public generatedMetaMessage: string = '';
    public preparingYoutube: boolean = false;
    public youtubePreview: any = null;
    public youtubeMessage: string = '';

    public async ngOnInit() {
        await this.service.init();
        await this.loadOptions();
        this.syncFromLocation();
        await this.load();
    }

    public syncFromLocation() {
        let params = new URLSearchParams(location.search);
        this.filters.text = params.get('text') || '';
        this.filters.status = params.get('status') || '';
        this.filters.category = params.get('category') || '';
        this.filters.tag = params.get('tag') || '';
        this.page = Number(params.get('page') || 1);
    }

    public async loadOptions() {
        let { code, data } = await wiz.call('options', {});
        if (code === 200) {
            this.options = data;
        }
    }

    public async load(page: number = this.page) {
        this.loading = true;
        this.message = '';
        this.page = page;
        await this.service.render();
        let response = await this.request('', 'GET', null, {
            page: this.page,
            dump: this.dump,
            text: this.filters.text,
            status: this.filters.status,
            category: this.filters.category,
            tag: this.filters.tag,
            sort: this.filters.sort,
        });
        this.loading = false;
        if (response.code === 200) {
            this.items = response.data.items || [];
            this.total = response.data.total || 0;
            this.updateUrl();
        } else {
            this.message = response.data.message || '레시피 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public updateUrl() {
        let params = new URLSearchParams();
        for (let key of ['text', 'status', 'category', 'tag']) {
            if (this.filters[key]) params.set(key, this.filters[key]);
        }
        if (this.page > 1) params.set('page', String(this.page));
        let query = params.toString();
        history.replaceState(null, '', query ? `/admin/recipes?${query}` : '/admin/recipes');
    }

    public async search() {
        await this.load(1);
    }

    public async resetFilters() {
        this.filters = { text: '', status: '', category: '', tag: '', sort: 'latest' };
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

    public async openNew() {
        this.formOpen = true;
        this.formMessage = '';
        this.generatedMeta = null;
        this.generatedMetaMessage = '';
        this.youtubePreview = null;
        this.youtubeMessage = '';
        this.versions = [];
        this.selectedVersionId = '';
        this.dishForm = this.blankDish();
        this.versionForm = this.blankVersion();
        await this.service.render();
    }

    public async edit(item: any) {
        this.formOpen = true;
        this.formMessage = '';
        this.generatedMeta = null;
        this.generatedMetaMessage = '';
        this.youtubePreview = null;
        this.youtubeMessage = '';
        this.dishForm = this.dishToForm(item);
        this.versionForm = this.blankVersion(item.name);
        this.versions = [];
        this.selectedVersionId = '';
        await this.service.render();
        await this.loadDetail(item.id);
    }

    public async closeForm() {
        this.formOpen = false;
        this.formMessage = '';
        this.generatedMeta = null;
        this.generatedMetaMessage = '';
        this.youtubePreview = null;
        this.youtubeMessage = '';
        await this.service.render();
    }

    public async loadDetail(dishId: string) {
        let detail = await this.request(`/${dishId}`, 'GET');
        let versions = await this.request(`/${dishId}/versions`, 'GET', null, { page: 1, dump: 50 });
        if (detail.code === 200) {
            this.dishForm = this.dishToForm(detail.data.dish);
        }
        if (versions.code === 200) {
            this.versions = versions.data.versions || [];
            if (this.versions.length) {
                let first = this.versions[0];
                this.selectedVersionId = first.id;
                this.versionForm = this.versionToForm(first);
            }
        }
        await this.service.render();
    }

    public async selectVersion(version: any) {
        this.selectedVersionId = version.id;
        this.versionForm = this.versionToForm(version);
        await this.service.render();
    }

    public async save() {
        if (this.saving) return;
        this.formMessage = '';
        if (!this.dishForm.name.trim()) {
            this.formMessage = '레시피 이름을 입력해주세요.';
            await this.service.render();
            return;
        }
        this.saving = true;
        await this.service.render();
        let dishPayload = this.dishPayload();
        let dishResponse = this.dishForm.id
            ? await this.request(`/${this.dishForm.id}`, 'PUT', dishPayload)
            : await this.request('', 'POST', dishPayload);
        if (dishResponse.code < 200 || dishResponse.code >= 300) {
            this.saving = false;
            this.formMessage = dishResponse.data.message || '레시피 저장에 실패했습니다.';
            await this.service.render();
            return;
        }
        let dish = dishResponse.data.dish;
        this.dishForm = this.dishToForm(dish);
        let versionPayload = this.versionPayload();
        let versionResponse = this.versionForm.id
            ? await this.request(`/${dish.id}/versions/${this.versionForm.id}`, 'PUT', versionPayload)
            : await this.request(`/${dish.id}/versions`, 'POST', versionPayload);
        this.saving = false;
        if (versionResponse.code < 200 || versionResponse.code >= 300) {
            this.formMessage = versionResponse.data.message || '버전 저장에 실패했습니다.';
            await this.service.render();
            return;
        }
        this.formMessage = '저장했습니다.';
        await this.loadDetail(dish.id);
        await this.load(this.page);
    }

    public async changeDishStatus(item: any, status: string) {
        let previous = item.status;
        item.status = status;
        await this.service.render();
        let response = await this.request(`/${item.id}`, 'PUT', { status });
        if (response.code !== 200) {
            item.status = previous;
            this.message = response.data.message || '상태 변경에 실패했습니다.';
        }
        await this.service.render();
    }

    public async hideDish(item: any) {
        if (!confirm(`'${item.name}' 레시피를 숨김 처리할까요?`)) return;
        let response = await this.request(`/${item.id}`, 'DELETE');
        if (response.code === 200) {
            await this.load(this.page);
            return;
        }
        this.message = response.data.message || '숨김 처리에 실패했습니다.';
        await this.service.render();
    }

    public async hideVersion() {
        if (!this.dishForm.id || !this.versionForm.id) return;
        if (!confirm('선택한 버전을 숨김 처리할까요?')) return;
        let response = await this.request(`/${this.dishForm.id}/versions/${this.versionForm.id}`, 'DELETE');
        if (response.code === 200) {
            await this.loadDetail(this.dishForm.id);
            return;
        }
        this.formMessage = response.data.message || '버전 숨김 처리에 실패했습니다.';
        await this.service.render();
    }

    public async createVersion() {
        this.selectedVersionId = '';
        this.versionForm = this.blankVersion(this.dishForm.name);
        await this.service.render();
    }

    public async generateMeta() {
        if (this.generatingMeta) return;
        this.generatedMetaMessage = '';
        if (!this.dishForm.id) {
            this.generatedMetaMessage = 'AI 생성 전에 레시피를 먼저 저장해주세요.';
            await this.service.render();
            return;
        }
        this.generatingMeta = true;
        await this.service.render();
        let { code, data } = await wiz.call('generate_meta', { dishId: this.dishForm.id });
        this.generatingMeta = false;
        if (code === 200) {
            this.generatedMeta = data.generated || null;
            await this.service.render();
            return;
        }
        this.generatedMetaMessage = data.message || 'AI 생성에 실패했습니다.';
        await this.service.render();
    }

    public async applyGenerated(field: string) {
        if (!this.generatedMeta) return;
        if (field === 'title') {
            this.dishForm.name = this.generatedMeta.title || this.dishForm.name;
            this.versionForm.title = this.generatedMeta.title || this.versionForm.title;
        }
        if (field === 'description') {
            this.dishForm.description = this.generatedMeta.description || this.dishForm.description;
            this.versionForm.summary = this.generatedMeta.description || this.versionForm.summary;
        }
        if (field === 'script') {
            let script = this.generatedMeta.script || '';
            if (script) {
                this.versionForm.cookingTipsText = this.versionForm.cookingTipsText
                    ? `${this.versionForm.cookingTipsText}\n\n${script}`
                    : script;
            }
        }
        await this.service.render();
    }

    public async prepareYoutubeUpload() {
        if (this.preparingYoutube) return;
        this.youtubeMessage = '';
        this.youtubePreview = null;
        if (!this.dishForm.id) {
            this.youtubeMessage = '유튜브 업로드 준비 전에 레시피를 먼저 저장해주세요.';
            await this.service.render();
            return;
        }
        this.preparingYoutube = true;
        await this.service.render();
        let { code, data } = await wiz.call('youtube_metadata', { dishId: this.dishForm.id });
        this.preparingYoutube = false;
        if (code === 200) {
            this.youtubePreview = data.metadata || null;
            await this.service.render();
            return;
        }
        this.youtubeMessage = data.message || '유튜브 업로드 메타데이터 생성에 실패했습니다.';
        await this.service.render();
    }

    public async closeYoutubePreview() {
        this.youtubePreview = null;
        this.youtubeMessage = '';
        await this.service.render();
    }

    public async toggleTag(tag: string) {
        let tags = this.dishForm.tags || [];
        if (tags.indexOf(tag) >= 0) {
            this.dishForm.tags = tags.filter((item: string) => item !== tag);
        } else {
            this.dishForm.tags = tags.concat([tag]);
        }
        await this.service.render();
    }

    public isTagSelected(tag: string) {
        return (this.dishForm.tags || []).indexOf(tag) >= 0;
    }

    public statusLabel(status: string) {
        let item = (this.options.recipeStatuses || []).find((option: any) => option.value === status);
        return item ? item.label : status;
    }

    public statusClass(status: string) {
        if (status === 'approved') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
        if (status === 'pending_review' || status === 'crawled' || status === 'ai_parsed' || status === 'ai_modified') return 'bg-amber-50 text-amber-700 border-amber-200';
        if (status === 'rejected') return 'bg-rose-50 text-rose-700 border-rose-200';
        if (status === 'hidden') return 'bg-zinc-100 text-zinc-500 border-zinc-200';
        return 'bg-sky-50 text-sky-700 border-sky-200';
    }

    public blankDish() {
        return {
            id: '',
            name: '',
            description: '',
            category: '일반',
            tags: [],
            thumbnailUrl: '',
            status: 'draft',
        };
    }

    public blankVersion(title: string = '') {
        return {
            id: '',
            title: title || '',
            sourceType: 'direct',
            sourceUrl: '',
            sourceTitle: '',
            sourceAuthor: '',
            summary: '',
            ingredientsText: '',
            stepsText: '',
            cookingTipsText: '',
            failurePreventionTipsText: '',
            substitutionTipsText: '',
            nutritionText: '{}',
            sodiumText: '{}',
            allergenText: '',
            difficulty: 'normal',
            cookingTime: 0,
            servingSize: '',
            status: 'draft',
        };
    }

    public dishToForm(dish: any) {
        return {
            id: dish.id || '',
            name: dish.name || '',
            description: dish.description || '',
            category: dish.category || '일반',
            tags: dish.tags || [],
            thumbnailUrl: dish.thumbnailUrl || '',
            status: dish.status || 'draft',
        };
    }

    public versionToForm(version: any) {
        return {
            id: version.id || '',
            title: version.title || this.dishForm.name || '',
            sourceType: version.sourceType || 'direct',
            sourceUrl: version.sourceUrl || '',
            sourceTitle: version.sourceTitle || '',
            sourceAuthor: version.sourceAuthor || '',
            summary: version.summary || '',
            ingredientsText: this.joinLines(version.ingredients),
            stepsText: this.joinLines(version.steps),
            cookingTipsText: this.joinLines(version.cookingTips),
            failurePreventionTipsText: this.joinLines(version.failurePreventionTips),
            substitutionTipsText: this.joinLines(version.substitutionTips),
            nutritionText: this.prettyJson(version.nutritionInfo || {}),
            sodiumText: this.prettyJson(version.sodiumInfo || {}),
            allergenText: this.joinLines(version.allergenInfo),
            difficulty: version.difficulty || 'normal',
            cookingTime: version.cookingTime || 0,
            servingSize: version.servingSize || '',
            status: version.status || 'draft',
        };
    }

    public dishPayload() {
        return {
            name: this.dishForm.name.trim(),
            description: this.dishForm.description,
            category: this.dishForm.category,
            tags: this.dishForm.tags || [],
            thumbnailUrl: this.dishForm.thumbnailUrl,
            status: this.dishForm.status,
        };
    }

    public versionPayload() {
        return {
            title: (this.versionForm.title || this.dishForm.name).trim(),
            sourceType: this.versionForm.sourceType,
            sourceUrl: this.versionForm.sourceUrl,
            sourceTitle: this.versionForm.sourceTitle,
            sourceAuthor: this.versionForm.sourceAuthor,
            summary: this.versionForm.summary,
            ingredients: this.splitLines(this.versionForm.ingredientsText),
            steps: this.splitLines(this.versionForm.stepsText),
            cookingTips: this.splitLines(this.versionForm.cookingTipsText),
            failurePreventionTips: this.splitLines(this.versionForm.failurePreventionTipsText),
            substitutionTips: this.splitLines(this.versionForm.substitutionTipsText),
            nutritionInfo: this.parseJsonObject(this.versionForm.nutritionText),
            sodiumInfo: this.parseJsonObject(this.versionForm.sodiumText),
            allergenInfo: this.splitLines(this.versionForm.allergenText),
            difficulty: this.versionForm.difficulty,
            cookingTime: Number(this.versionForm.cookingTime || 0),
            servingSize: this.versionForm.servingSize,
            status: this.versionForm.status,
        };
    }

    public splitLines(value: string) {
        return String(value || '').split('\n').map((item) => item.trim()).filter((item) => item);
    }

    public joinLines(value: any[]) {
        return Array.isArray(value) ? value.join('\n') : '';
    }

    public prettyJson(value: any) {
        try {
            return JSON.stringify(value || {}, null, 2);
        } catch (error) {
            return '{}';
        }
    }

    public parseJsonObject(value: string) {
        try {
            let parsed = JSON.parse(value || '{}');
            return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
        } catch (error) {
            return {};
        }
    }

    public async request(path: string, method: string = 'GET', data: any = null, query: any = null) {
        let url = `/api/admin/recipes${path || ''}`;
        if (query) {
            let params = new URLSearchParams();
            Object.keys(query).forEach((key) => {
                if (query[key] !== undefined && query[key] !== null && query[key] !== '') {
                    params.set(key, String(query[key]));
                }
            });
            let qs = params.toString();
            if (qs) url += `?${qs}`;
        }
        let csrfToken = (window as any).recipeCsrfToken || '';
        let init: any = {
            method,
            headers: csrfToken ? { 'X-CSRF-Token': csrfToken } : {},
        };
        if (method !== 'GET' && data !== null) {
            let body = new URLSearchParams();
            body.set('data', JSON.stringify(data));
            init.body = body;
        }
        let response = await fetch(url, init);
        let payload: any = {};
        try {
            payload = await response.json();
        } catch (error) {
            payload = {};
        }
        return {
            code: payload.code || response.status,
            data: payload.data || payload,
        };
    }
}
