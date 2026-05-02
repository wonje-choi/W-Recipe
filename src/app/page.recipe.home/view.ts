import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public query: string = '';
    public loading: boolean = true;
    public recommended: any[] = [];
    public popular: any[] = [];
    public randomItems: any[] = [];
    public latest: any[] = [];
    public keywords: string[] = [];

    public fallbackImages: string[] = [
        'https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80',
    ];

    public dietPanels: any[] = [
        {
            title: '저염레시피',
            href: '/recipes/low-sodium',
            before: '간장 2큰술, 소금 간 중심',
            after: '향신채와 산미로 간을 낮춘 버전',
            accent: 'emerald',
        },
        {
            title: '이유식레시피',
            href: '/recipes/baby-food',
            before: '성인 기준 식감과 간',
            after: '월령, 질감, 알레르기 주의 표시',
            accent: 'amber',
        },
    ];

    public async ngOnInit() {
        await this.service.init();
        await this.load();
    }

    public async load() {
        this.loading = true;
        await this.service.render();
        let { code, data } = await wiz.call('load', {});
        this.loading = false;
        if (code === 200) {
            this.recommended = data.recommended || [];
            this.popular = data.popular || [];
            this.randomItems = data.randomItems || [];
            this.latest = data.latest || [];
            this.keywords = data.keywords || [];
        }
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

    public search(text: string = '') {
        let query = (text || this.query || '').trim();
        let suffix = query ? `?text=${encodeURIComponent(query)}` : '';
        location.href = `/recipes${suffix}`;
    }

    public go(href: string) {
        location.href = href;
    }

    public openDish(item: any) {
        if (!item || !item.id) return;
        location.href = `/recipes/detail/${item.id}`;
    }
}
