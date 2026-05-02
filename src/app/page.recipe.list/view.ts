import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public filtersOpen: boolean = false;
    public items: any[] = [];
    public categories: string[] = [];
    public tags: string[] = [];
    public total: number = 0;
    public page: number = 1;
    public dump: number = 12;
    public totalPages: number = 1;
    public lowSodium: any = {
        enabled: false,
        healthNotice: '',
        flavorComplements: [],
    };
    public babyFood: any = {
        enabled: false,
        stages: {},
        selectedStage: '',
        guardianNotice: '',
        safetyKeywords: [],
    };
    public filters: any = {
        text: '',
        preset: '',
        category: '',
        tag: '',
        sort: 'latest',
        babyStage: '',
    };

    public sortOptions: any[] = [
        { label: '조회수순', value: 'view_count' },
        { label: '최신순', value: 'latest' },
        { label: '인기순', value: 'popular' },
        { label: '난이도순', value: 'difficulty' },
        { label: '조리시간순', value: 'cooking_time' },
        { label: 'AI 개량순', value: 'ai_modified' },
    ];

    public presetOptions: any[] = [
        { label: '전체', value: '', href: '/recipes' },
        { label: '저염레시피', value: 'low-sodium', href: '/recipes/low-sodium' },
        { label: '이유식레시피', value: 'baby-food', href: '/recipes/baby-food' },
    ];

    public fallbackImages: string[] = [
        'https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80',
    ];

    public async ngOnInit() {
        await this.service.init();
        this.syncFromLocation();
        await this.load();
    }

    public syncFromLocation() {
        let params = new URLSearchParams(location.search);
        let parts = location.pathname.split('/').filter((item) => item);
        this.filters.preset = parts[1] || '';
        this.filters.text = params.get('text') || '';
        this.filters.category = params.get('category') || '';
        this.filters.tag = params.get('tag') || '';
        this.filters.sort = params.get('sort') || this.filters.sort;
        this.filters.babyStage = params.get('babyStage') || '';
        this.page = Number(params.get('page') || 1);
    }

    public async load() {
        this.loading = true;
        await this.service.render();
        let { code, data } = await wiz.call('search', {
            page: this.page,
            dump: this.dump,
            text: this.filters.text,
            preset: this.filters.preset,
            category: this.filters.category,
            tag: this.filters.tag,
            sort: this.filters.sort,
            babyStage: this.filters.babyStage,
        });
        this.loading = false;
        if (code === 200) {
            this.items = data.items || [];
            this.total = data.total || 0;
            this.categories = data.categories || [];
            this.tags = data.tags || [];
            this.lowSodium = data.lowSodium || this.lowSodium;
            this.babyFood = data.babyFood || this.babyFood;
            this.filters = Object.assign(this.filters, data.filters || {});
            this.totalPages = Math.max(1, Math.ceil(this.total / this.dump));
        }
        await this.service.render();
    }

    public buildUrl(page: number = 1) {
        let base = this.filters.preset ? `/recipes/${this.filters.preset}` : '/recipes';
        let params = new URLSearchParams();
        if (this.filters.text) params.set('text', this.filters.text);
        if (this.filters.category && !this.filters.preset) params.set('category', this.filters.category);
        if (this.filters.tag && !this.filters.preset) params.set('tag', this.filters.tag);
        if (this.filters.babyStage && this.filters.preset === 'baby-food') params.set('babyStage', this.filters.babyStage);
        if (this.filters.sort && this.filters.sort !== 'latest') params.set('sort', this.filters.sort);
        if (page > 1) params.set('page', String(page));
        let query = params.toString();
        return query ? `${base}?${query}` : base;
    }

    public applyFilters() {
        location.href = this.buildUrl(1);
    }

    public resetFilters() {
        location.href = '/recipes';
    }

    public goPreset(option: any) {
        location.href = option.href;
    }

    public goPage(nextPage: number) {
        if (nextPage < 1 || nextPage > this.totalPages) return;
        location.href = this.buildUrl(nextPage);
    }

    public async toggleFilters() {
        this.filtersOpen = !this.filtersOpen;
        await this.service.render();
    }

    public imageFor(item: any, index: number) {
        return item.thumbnailUrl || this.fallbackImages[index % this.fallbackImages.length];
    }

    public imageStyle(item: any, index: number) {
        let fallback = this.fallbackImages[index % this.fallbackImages.length];
        let image = this.imageFor(item, index);
        if (image === fallback) return `url('${fallback}')`;
        return `url('${image}'), url('${fallback}')`;
    }

    public isLowSodiumPreset() {
        return this.filters.preset === 'low-sodium';
    }

    public lowSodiumPreview(item: any) {
        return (item && item.lowSodiumPreview) || {
            sodiumPoints: [],
            sodiumIngredients: [],
            flavorTips: [],
            aiModified: false,
        };
    }

    public isBabyFoodPreset() {
        return this.filters.preset === 'baby-food';
    }

    public babyStageOptions() {
        let stages = (this.babyFood && this.babyFood.stages) || {};
        return Object.keys(stages).map((key) => Object.assign({ value: key }, stages[key]));
    }

    public selectedBabyStageLabel() {
        let stages = (this.babyFood && this.babyFood.stages) || {};
        let selected = stages[this.filters.babyStage];
        return selected ? selected.label : this.filters.babyStage;
    }

    public goBabyStage(stage: string) {
        this.filters.babyStage = stage;
        location.href = this.buildUrl(1);
    }

    public babyPreview(item: any) {
        return (item && item.babyPreview) || {
            stageLabel: '',
            recommendedAge: '',
            particleSize: '',
            storage: '',
            freezing: '',
            allergens: [],
            warnings: [],
            aiModified: false,
        };
    }

    public openDish(item: any) {
        if (!item || !item.id) return;
        location.href = `/recipes/detail/${item.id}`;
    }
}
