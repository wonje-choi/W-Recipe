import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public loading: boolean = true;
    public actionLoading: string = '';
    public message: string = '';
    public activeTab: string = 'comments';
    public selected: any = null;
    public selectedType: string = 'comment';
    public memoDraft: string = '';
    public dump: number = 12;

    public summary: any = {
        comments: 0,
        reportedComments: 0,
        openReports: 0,
        openEditRequests: 0,
        premiumMembers: 0,
    };

    public options: any = {
        commentStatuses: [],
        editRequestStatuses: [],
        editRequestTypes: [],
        reportStatuses: [],
        reportTargetTypes: [],
        reportReasons: [],
        userStatuses: [],
        subscriptionPlans: [],
        expertStatuses: [],
        expertAssignmentStatuses: [],
        experts: [],
    };

    public tabs: any[] = [
        { key: 'comments', label: '댓글' },
        { key: 'reports', label: '신고' },
        { key: 'edit-requests', label: '수정 요청' },
        { key: 'members', label: '구독' },
        { key: 'experts', label: '전문가' },
    ];

    public commentItems: any[] = [];
    public reportItems: any[] = [];
    public editItems: any[] = [];
    public memberItems: any[] = [];
    public expertItems: any[] = [];
    public commentPage: number = 1;
    public reportPage: number = 1;
    public editPage: number = 1;
    public memberPage: number = 1;
    public expertPage: number = 1;
    public commentTotal: number = 0;
    public reportTotal: number = 0;
    public editTotal: number = 0;
    public memberTotal: number = 0;
    public expertTotal: number = 0;

    public commentFilters: any = {
        text: '',
        status: '',
        reportedOnly: false,
    };

    public reportFilters: any = {
        text: '',
        status: '',
        targetType: '',
    };

    public editFilters: any = {
        text: '',
        status: '',
        requestType: '',
    };

    public memberFilters: any = {
        text: '',
        plan: '',
    };

    public expertFilters: any = {
        text: '',
        status: '',
    };

    public async ngOnInit() {
        await this.service.init();
        this.syncFromLocation();
        await this.loadOptions();
        await this.load();
    }

    public syncFromLocation() {
        let params = new URLSearchParams(location.search);
        let tab = params.get('tab') || 'comments';
        if (this.tabs.find((item) => item.key === tab)) this.activeTab = tab;
        let status = params.get('status') || '';
        let text = params.get('text') || '';
        if (this.activeTab === 'reports') {
            this.reportFilters.status = status;
            this.reportFilters.text = text;
            this.reportFilters.targetType = params.get('targetType') || '';
            this.reportPage = Number(params.get('page') || 1);
        } else if (this.activeTab === 'edit-requests') {
            this.editFilters.status = status;
            this.editFilters.text = text;
            this.editFilters.requestType = params.get('requestType') || '';
            this.editPage = Number(params.get('page') || 1);
        } else if (this.activeTab === 'members') {
            this.memberFilters.plan = params.get('plan') || '';
            this.memberFilters.text = text;
            this.memberPage = Number(params.get('page') || 1);
        } else if (this.activeTab === 'experts') {
            this.expertFilters.status = status;
            this.expertFilters.text = text;
            this.expertPage = Number(params.get('page') || 1);
        } else {
            this.commentFilters.status = status;
            this.commentFilters.text = text;
            this.commentFilters.reportedOnly = params.get('reportedOnly') === 'true';
            this.commentPage = Number(params.get('page') || 1);
        }
    }

    public updateUrl() {
        let params = new URLSearchParams();
        if (this.activeTab !== 'comments') params.set('tab', this.activeTab);
        if (this.activeTab === 'reports') {
            if (this.reportFilters.text) params.set('text', this.reportFilters.text);
            if (this.reportFilters.status) params.set('status', this.reportFilters.status);
            if (this.reportFilters.targetType) params.set('targetType', this.reportFilters.targetType);
            if (this.reportPage > 1) params.set('page', String(this.reportPage));
        } else if (this.activeTab === 'edit-requests') {
            if (this.editFilters.text) params.set('text', this.editFilters.text);
            if (this.editFilters.status) params.set('status', this.editFilters.status);
            if (this.editFilters.requestType) params.set('requestType', this.editFilters.requestType);
            if (this.editPage > 1) params.set('page', String(this.editPage));
        } else if (this.activeTab === 'members') {
            if (this.memberFilters.text) params.set('text', this.memberFilters.text);
            if (this.memberFilters.plan) params.set('plan', this.memberFilters.plan);
            if (this.memberPage > 1) params.set('page', String(this.memberPage));
        } else if (this.activeTab === 'experts') {
            if (this.expertFilters.text) params.set('text', this.expertFilters.text);
            if (this.expertFilters.status) params.set('status', this.expertFilters.status);
            if (this.expertPage > 1) params.set('page', String(this.expertPage));
        } else {
            if (this.commentFilters.text) params.set('text', this.commentFilters.text);
            if (this.commentFilters.status) params.set('status', this.commentFilters.status);
            if (this.commentFilters.reportedOnly) params.set('reportedOnly', 'true');
            if (this.commentPage > 1) params.set('page', String(this.commentPage));
        }
        let query = params.toString();
        history.replaceState(null, '', query ? `/admin/feedback?${query}` : '/admin/feedback');
    }

    public async loadOptions() {
        let { code, data } = await wiz.call('options', {});
        if (code === 200) {
            this.options = data;
        } else {
            this.message = data.message || '옵션을 불러오지 못했습니다.';
        }
    }

    public async selectTab(tab: string) {
        this.activeTab = tab;
        this.selected = null;
        this.memoDraft = '';
        await this.load(1);
    }

    public async load(page?: number) {
        if (this.activeTab === 'reports') return await this.loadReports(page || this.reportPage);
        if (this.activeTab === 'edit-requests') return await this.loadEditRequests(page || this.editPage);
        if (this.activeTab === 'members') return await this.loadMembers(page || this.memberPage);
        if (this.activeTab === 'experts') return await this.loadExperts(page || this.expertPage);
        return await this.loadComments(page || this.commentPage);
    }

    public async loadComments(page: number = this.commentPage) {
        this.loading = true;
        this.message = '';
        this.commentPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('comments', {
            page: this.commentPage,
            dump: this.dump,
            text: this.commentFilters.text,
            status: this.commentFilters.status,
            reportedOnly: this.commentFilters.reportedOnly,
        });
        this.loading = false;
        if (code === 200) {
            this.commentItems = data.items || [];
            this.commentTotal = data.total || 0;
            this.summary = data.summary || this.summary;
            this.refreshSelection(this.commentItems, 'comment');
        } else {
            this.message = data.message || '댓글 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async loadReports(page: number = this.reportPage) {
        this.loading = true;
        this.message = '';
        this.reportPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('reports', {
            page: this.reportPage,
            dump: this.dump,
            text: this.reportFilters.text,
            status: this.reportFilters.status,
            targetType: this.reportFilters.targetType,
        });
        this.loading = false;
        if (code === 200) {
            this.reportItems = data.items || [];
            this.reportTotal = data.total || 0;
            this.summary = data.summary || this.summary;
            this.refreshSelection(this.reportItems, 'report');
        } else {
            this.message = data.message || '신고 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async loadEditRequests(page: number = this.editPage) {
        this.loading = true;
        this.message = '';
        this.editPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('edit_requests', {
            page: this.editPage,
            dump: this.dump,
            text: this.editFilters.text,
            status: this.editFilters.status,
            requestType: this.editFilters.requestType,
        });
        this.loading = false;
        if (code === 200) {
            this.editItems = data.items || [];
            this.editTotal = data.total || 0;
            this.summary = data.summary || this.summary;
            this.refreshSelection(this.editItems, 'edit');
        } else {
            this.message = data.message || '수정 요청 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async loadMembers(page: number = this.memberPage) {
        this.loading = true;
        this.message = '';
        this.memberPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('members', {
            page: this.memberPage,
            dump: this.dump,
            text: this.memberFilters.text,
            plan: this.memberFilters.plan,
        });
        this.loading = false;
        if (code === 200) {
            this.memberItems = data.items || [];
            this.memberTotal = data.total || 0;
            this.summary = data.summary || this.summary;
            this.refreshSelection(this.memberItems, 'member');
        } else {
            this.message = data.message || '구독 회원 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public async loadExperts(page: number = this.expertPage) {
        this.loading = true;
        this.message = '';
        this.expertPage = page;
        this.updateUrl();
        await this.service.render();
        let { code, data } = await wiz.call('experts', {
            page: this.expertPage,
            dump: this.dump,
            text: this.expertFilters.text,
            status: this.expertFilters.status,
        });
        this.loading = false;
        if (code === 200) {
            this.expertItems = data.items || [];
            this.expertTotal = data.total || 0;
            this.summary = data.summary || this.summary;
            this.refreshSelection(this.expertItems, 'expert');
        } else {
            this.message = data.message || '전문가 목록을 불러오지 못했습니다.';
        }
        await this.service.render();
    }

    public refreshSelection(items: any[], type: string) {
        if (this.selected && this.selectedType === type) {
            let matched = items.find((item) => item.id === this.selected.id);
            if (matched) {
                this.selectItem(matched, type, false);
                return;
            }
        }
        if (items.length) this.selectItem(items[0], type, false);
        else this.selected = null;
    }

    public async search() {
        await this.load(1);
    }

    public async resetFilters() {
        if (this.activeTab === 'reports') this.reportFilters = { text: '', status: '', targetType: '' };
        else if (this.activeTab === 'edit-requests') this.editFilters = { text: '', status: '', requestType: '' };
        else if (this.activeTab === 'members') this.memberFilters = { text: '', plan: '' };
        else if (this.activeTab === 'experts') this.expertFilters = { text: '', status: '' };
        else this.commentFilters = { text: '', status: '', reportedOnly: false };
        await this.load(1);
    }

    public selectItem(item: any, type: string, render: boolean = true) {
        this.selected = item;
        this.selectedType = type;
        this.memoDraft = item && item.adminMemo ? item.adminMemo : '';
        if (render) this.service.render();
    }

    public totalPages(total: number) {
        return Math.max(1, Math.ceil(total / this.dump));
    }

    public async prevPage() {
        if (this.activeTab === 'reports' && this.reportPage > 1) await this.loadReports(this.reportPage - 1);
        else if (this.activeTab === 'edit-requests' && this.editPage > 1) await this.loadEditRequests(this.editPage - 1);
        else if (this.activeTab === 'members' && this.memberPage > 1) await this.loadMembers(this.memberPage - 1);
        else if (this.activeTab === 'experts' && this.expertPage > 1) await this.loadExperts(this.expertPage - 1);
        else if (this.activeTab === 'comments' && this.commentPage > 1) await this.loadComments(this.commentPage - 1);
    }

    public async nextPage() {
        if (this.activeTab === 'reports' && this.reportPage < this.totalPages(this.reportTotal)) await this.loadReports(this.reportPage + 1);
        else if (this.activeTab === 'edit-requests' && this.editPage < this.totalPages(this.editTotal)) await this.loadEditRequests(this.editPage + 1);
        else if (this.activeTab === 'members' && this.memberPage < this.totalPages(this.memberTotal)) await this.loadMembers(this.memberPage + 1);
        else if (this.activeTab === 'experts' && this.expertPage < this.totalPages(this.expertTotal)) await this.loadExperts(this.expertPage + 1);
        else if (this.activeTab === 'comments' && this.commentPage < this.totalPages(this.commentTotal)) await this.loadComments(this.commentPage + 1);
    }

    public currentPage() {
        if (this.activeTab === 'reports') return this.reportPage;
        if (this.activeTab === 'edit-requests') return this.editPage;
        if (this.activeTab === 'members') return this.memberPage;
        if (this.activeTab === 'experts') return this.expertPage;
        return this.commentPage;
    }

    public currentTotal() {
        if (this.activeTab === 'reports') return this.reportTotal;
        if (this.activeTab === 'edit-requests') return this.editTotal;
        if (this.activeTab === 'members') return this.memberTotal;
        if (this.activeTab === 'experts') return this.expertTotal;
        return this.commentTotal;
    }

    public async toggleReportedOnly() {
        this.commentFilters.reportedOnly = !this.commentFilters.reportedOnly;
        await this.loadComments(1);
    }

    public async commentAction(action: string, item: any = this.selected) {
        if (!item || !item.id) return;
        if (action === 'delete' && !confirm('이 댓글을 삭제 상태로 변경할까요?')) return;
        this.actionLoading = `${item.id}:${action}`;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('comment_action', {
            id: item.id,
            action,
            reason: this.memoDraft,
        });
        this.actionLoading = '';
        if (code === 200) {
            if (this.activeTab === 'comments' && data.comment) this.selectItem(data.comment, 'comment', false);
            await this.load(this.currentPage());
            return;
        }
        this.message = data.message || '댓글 상태 변경에 실패했습니다.';
        await this.service.render();
    }

    public async reportAction(status: string, item: any = this.selected) {
        if (!item || !item.id) return;
        this.actionLoading = `${item.id}:${status}`;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('report_action', {
            id: item.id,
            status,
            adminMemo: this.memoDraft,
        });
        this.actionLoading = '';
        if (code === 200) {
            if (data.report) this.selectItem(data.report, 'report', false);
            await this.loadReports(this.reportPage);
            return;
        }
        this.message = data.message || '신고 처리에 실패했습니다.';
        await this.service.render();
    }

    public async editRequestAction(status: string, item: any = this.selected) {
        if (!item || !item.id) return;
        this.actionLoading = `${item.id}:${status}`;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('edit_request_action', {
            id: item.id,
            status,
            adminMemo: this.memoDraft,
        });
        this.actionLoading = '';
        if (code === 200) {
            if (data.editRequest) this.selectItem(data.editRequest, 'edit', false);
            await this.loadEditRequests(this.editPage);
            return;
        }
        this.message = data.message || '수정 요청 처리에 실패했습니다.';
        await this.service.render();
    }

    public subjectUser(item: any = this.selected) {
        if (!item) return null;
        if (this.selectedType === 'member') return item;
        if (this.selectedType === 'report' && item.target && item.target.user && item.target.user.id) return item.target.user;
        if (item.user && item.user.id) return item.user;
        if (item.reporter && item.reporter.id) return item.reporter;
        return null;
    }

    public async suspendUser(user: any = this.subjectUser()) {
        if (!user || !user.id) return;
        let label = user.nickname || user.email || user.id;
        if (!confirm(`${label} 사용자를 정지 처리할까요?`)) return;
        this.actionLoading = `${user.id}:suspend`;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('user_action', {
            userId: user.id,
            status: 'suspended',
        });
        this.actionLoading = '';
        if (code === 200) {
            await this.load(this.currentPage());
            return;
        }
        this.message = data.message || '사용자 제재에 실패했습니다.';
        await this.service.render();
    }

    public async saveSubscription(user: any = this.selected) {
        if (!user || !user.id) return;
        this.actionLoading = `${user.id}:subscription`;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('subscription_action', {
            userId: user.id,
            plan: user.subscriptionPlan || 'free',
            expiresAt: user.subscriptionExpiresAt || '',
        });
        this.actionLoading = '';
        if (code === 200) {
            if (data.member) this.selectItem(data.member, 'member', false);
            await this.loadMembers(this.memberPage);
            return;
        }
        this.message = data.message || '구독 플랜 저장에 실패했습니다.';
        await this.service.render();
    }

    public newExpert() {
        this.selectItem({
            id: '',
            name: '',
            email: '',
            specialty: '',
            status: 'active',
            statusLabel: '활성',
        }, 'expert');
    }

    public async saveExpert(expert: any = this.selected) {
        if (!expert) return;
        this.actionLoading = `${expert.id || 'new'}:expert`;
        this.message = '';
        await this.service.render();
        let { code, data } = await wiz.call('expert_action', expert);
        this.actionLoading = '';
        if (code === 200) {
            if (data.options && data.options.experts) this.options.experts = data.options.experts;
            if (data.expert) this.selectItem(data.expert, 'expert', false);
            await this.loadExperts(this.expertPage);
            return;
        }
        this.message = data.message || '전문가 저장에 실패했습니다.';
        await this.service.render();
    }

    public async saveAssignment(item: any = this.selected) {
        if (!item || !item.id || !item.expertAssignment) return;
        this.actionLoading = `${item.id}:expert-assignment`;
        this.message = '';
        await this.service.render();
        let assignment = item.expertAssignment;
        let { code, data } = await wiz.call('assignment_action', {
            targetType: 'edit_request',
            targetId: item.id,
            expertId: assignment.expertId,
            status: assignment.status || 'assigned',
            reviewNote: assignment.reviewNote || '',
        });
        this.actionLoading = '';
        if (code === 200) {
            if (data.editRequest) this.selectItem(data.editRequest, 'edit', false);
            await this.loadEditRequests(this.editPage);
            return;
        }
        this.message = data.message || '전문가 배정 저장에 실패했습니다.';
        await this.service.render();
    }

    public subscriptionClass(plan: string) {
        if (plan === 'premium') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
        return 'border-zinc-200 bg-zinc-50 text-zinc-600';
    }

    public openRecipe(item: any = this.selected) {
        if (!item) return;
        let recipe = item.recipe || (item.target && item.target.recipe) || (item.target && item.target.comment && item.target.comment.recipe) || null;
        if (!recipe || !recipe.dishId) return;
        location.href = `/recipes/detail/${recipe.dishId}`;
    }

    public statusClass(status: string) {
        if (status === 'visible' || status === 'resolved' || status === 'actioned' || status === 'active') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
        if (status === 'hidden' || status === 'in_review' || status === 'reported' || status === 'open' || status === 'assigned') return 'border-amber-200 bg-amber-50 text-amber-700';
        if (status === 'deleted' || status === 'rejected' || status === 'suspended') return 'border-rose-200 bg-rose-50 text-rose-700';
        return 'border-zinc-200 bg-zinc-50 text-zinc-600';
    }

    public tabClass(tab: string) {
        return this.activeTab === tab ? 'border-emerald-600 bg-emerald-50 text-emerald-700' : 'border-zinc-200 bg-white text-zinc-600 hover:border-emerald-300';
    }

    public selectedTitle() {
        if (!this.selected) return '선택된 항목 없음';
        if (this.selectedType === 'comment') return this.selected.content || this.selected.id;
        if (this.selectedType === 'report') return this.selected.reasonLabel || this.selected.id;
        if (this.selectedType === 'member') return this.selected.nickname || this.selected.email || this.selected.id;
        if (this.selectedType === 'expert') return this.selected.name || '새 전문가';
        return this.selected.requestTypeLabel || this.selected.id;
    }
}
