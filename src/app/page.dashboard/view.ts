import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public metrics: any[] = [];
    public reviewQueue: any[] = [];
    public operations: any = this.defaultOperations();
    public message: string = '';

    public async ngOnInit() {
        await this.service.init();
        await this.load();
    }

    public defaultOperations() {
        return {
            daily: {
                visitors: 0,
                recipeViews: 0,
                signups: 0,
                comments: 0,
                reports: 0,
                aiRequests: 0,
            },
            reviewCounts: {
                dishPending: 0,
                versionPending: 0,
                aiPending: 0,
                editOpen: 0,
                reportOpen: 0,
                pendingTotal: 0,
            },
            popularRecipes: [],
            recentSources: [],
            failedLogs: [],
            sourceCount: 0,
            sourceErrors: 0,
            sourceFailureRate: 0,
            totalRecipeViews: 0,
            lowSodiumViews: 0,
            babyFoodViews: 0,
            comments: 0,
            todayComments: 0,
            reports: 0,
            todayReports: 0,
            signups: 0,
            todaySignups: 0,
            aiRequests: 0,
            aiTodayRequests: 0,
            aiFailed: 0,
            aiFailureRate: 0,
            tokenTotal: 0,
            costTotal: 0,
            approvalRate: 0,
            rejected: 0,
            approved: 0,
            measurementNote: '',
        };
    }

    public async load() {
        this.loading = true;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('overview', {});
        this.loading = false;
        if (code === 200) {
            this.metrics = data.metrics || [];
            this.reviewQueue = data.reviewQueue || [];
            this.operations = Object.assign(this.defaultOperations(), data.operations || {});
        } else {
            this.message = data.message || '대시보드를 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public go(href: string) {
        location.href = href;
    }

    public toneClass(tone: string) {
        let classes: any = {
            zinc: 'bg-zinc-50 text-zinc-700 border-zinc-200',
            amber: 'bg-amber-50 text-amber-700 border-amber-200',
            sky: 'bg-sky-50 text-sky-700 border-sky-200',
            emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
            violet: 'bg-violet-50 text-violet-700 border-violet-200',
            indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
        };
        return classes[tone] || classes.zinc;
    }
}
