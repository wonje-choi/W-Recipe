import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public searching: boolean = false;
    public submitting: boolean = false;
    public user: any = null;
    public recipeOptions: any[] = [];
    public purposeOptions: any[] = [];
    public targetUserTypes: string[] = [];
    public policy: any = null;
    public recipeQuery: string = '';
    public selectedRecipe: any = null;
    public message: string = '';
    public success: any = null;
    public form: any = {
        recipeVersionId: '',
        purpose: 'tastier',
        targetUserType: '일반',
        excludedIngredients: '',
        allergies: '',
        desiredCookingTime: '',
        tasteDirection: '',
        babyAgeMonth: '',
        sodiumPreference: '',
        texturePreference: '',
        additionalRequest: '',
    };

    public async ngOnInit() {
        await this.service.init();
        await this.load();
    }

    public async load() {
        this.loading = true;
        await this.service.render();
        let { code, data } = await wiz.call('load', { text: this.recipeQuery });
        this.loading = false;
        if (code === 200) {
            this.user = data.user;
            this.recipeOptions = data.recipeOptions || [];
            this.purposeOptions = data.purposes || [];
            this.targetUserTypes = data.targetUserTypes || [];
            this.policy = data.policy;
            if (this.recipeOptions.length > 0 && !this.selectedRecipe) {
                this.selectRecipe(this.recipeOptions[0]);
            }
        } else {
            this.message = data.message || 'AI 개량 요청 화면을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async searchRecipes() {
        this.searching = true;
        await this.service.render();
        let { code, data } = await wiz.call('search_recipes', { text: this.recipeQuery });
        this.searching = false;
        if (code === 200) {
            this.recipeOptions = data.recipeOptions || [];
            if (this.recipeOptions.length > 0) {
                this.selectRecipe(this.recipeOptions[0]);
            }
        } else {
            this.message = data.message || '대상 레시피 검색에 실패했습니다.';
        }
        await this.service.render();
    }

    public selectRecipe(item: any) {
        this.selectedRecipe = item;
        this.form.recipeVersionId = item ? item.recipeVersionId : '';
    }

    public selectPurpose(option: any) {
        this.form.purpose = option.value;
    }

    public isPurpose(value: string) {
        return this.form.purpose === value;
    }

    public selectedPurpose() {
        return this.purposeOptions.find((option) => option.value === this.form.purpose) || this.purposeOptions[0] || null;
    }

    public openLogin() {
        window.dispatchEvent(new CustomEvent('recipe-open-login', { detail: { tab: 'user' } }));
    }

    public canSubmit() {
        return !!this.user && !!this.form.recipeVersionId && !this.submitting;
    }

    public async submit() {
        this.message = '';
        this.success = null;
        if (!this.user) {
            this.message = '로그인이 필요합니다.';
            this.openLogin();
            await this.service.render();
            return;
        }
        if (!this.form.recipeVersionId) {
            this.message = '개량할 레시피를 선택해주세요.';
            await this.service.render();
            return;
        }
        this.submitting = true;
        await this.service.render();
        let { code, data } = await wiz.call('submit', this.form);
        this.submitting = false;
        if (code === 201) {
            this.success = data.modification;
            this.message = '';
            await this.service.render();
            return;
        }
        this.message = data.message || 'AI 개량 요청 저장에 실패했습니다.';
        await this.service.render();
    }
}
