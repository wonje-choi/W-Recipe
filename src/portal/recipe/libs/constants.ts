export const USER_ROLES = {
    GUEST: 'guest',
    USER: 'user',
    ADMIN: 'admin',
} as const;

export const USER_STATUSES = {
    ACTIVE: 'active',
    SUSPENDED: 'suspended',
    DELETED: 'deleted',
    PENDING: 'pending',
} as const;

export const RECIPE_STATUSES = {
    DRAFT: 'draft',
    CRAWLED: 'crawled',
    AI_PARSED: 'ai_parsed',
    AI_MODIFIED: 'ai_modified',
    PENDING_REVIEW: 'pending_review',
    APPROVED: 'approved',
    REJECTED: 'rejected',
    HIDDEN: 'hidden',
} as const;

export const AI_STATUSES = {
    QUEUED: 'queued',
    PROCESSING: 'processing',
    PENDING_REVIEW: 'pending_review',
    APPROVED: 'approved',
    REJECTED: 'rejected',
    FAILED: 'failed',
} as const;

export const AI_PROCESSING_STATUSES = {
    QUEUED: 'queued',
    PROCESSING: 'processing',
    COMPLETED: 'completed',
    FAILED: 'failed',
} as const;

export const AI_PROMPT_TYPES = {
    RECIPE_SUMMARY: 'recipe_summary',
    LOW_SODIUM: 'low_sodium',
    BABY_FOOD: 'baby_food',
    TASTE_IMPROVEMENT: 'taste_improvement',
    REVIEW_SUMMARY: 'review_summary',
} as const;

export const SOURCE_TYPES = {
    YOUTUBE: 'youtube',
    BLOG: 'blog',
    WEB: 'web',
    DIRECT: 'direct',
    AI_MODIFIED: 'ai_modified',
} as const;

export const COMMENT_STATUSES = {
    VISIBLE: 'visible',
    HIDDEN: 'hidden',
    DELETED: 'deleted',
    REPORTED: 'reported',
} as const;

export const EDIT_REQUEST_STATUSES = {
    OPEN: 'open',
    IN_REVIEW: 'in_review',
    RESOLVED: 'resolved',
    REJECTED: 'rejected',
} as const;

export const EDIT_REQUEST_TYPES = {
    ERROR: 'error',
    MEASUREMENT: 'measurement_issue',
    SOURCE: 'source_issue',
    TASTE_IMPROVEMENT: 'taste_improvement',
    OTHER: 'other',
} as const;

export const REPORT_STATUSES = {
    OPEN: 'open',
    IN_REVIEW: 'in_review',
    ACTIONED: 'actioned',
    REJECTED: 'rejected',
} as const;

export const REPORT_TARGET_TYPES = {
    COMMENT: 'comment',
    RECIPE_VERSION: 'recipe_version',
    RECIPE_DISH: 'recipe_dish',
} as const;

export const REPORT_REASONS = {
    SPAM: 'spam',
    INAPPROPRIATE: 'inappropriate',
    WRONG_INFO: 'wrong_info',
    SAFETY_ISSUE: 'safety_issue',
    COPYRIGHT: 'copyright',
    OTHER: 'other',
} as const;

export const CRAWLING_STATUSES = {
    PENDING: 'pending',
    ALLOWED: 'allowed',
    BLOCKED: 'blocked',
    COLLECTED: 'collected',
    SUMMARIZED: 'summarized',
    FAILED: 'failed',
    EXPIRED: 'expired',
} as const;

export const AI_PURPOSES = {
    TASTIER: 'tastier',
    LOW_SODIUM: 'low_sodium',
    BABY_FOOD: 'baby_food',
    DIET: 'diet',
    HIGH_PROTEIN: 'high_protein',
    SHORTER_TIME: 'shorter_time',
    SIMPLER_INGREDIENTS: 'simpler_ingredients',
    SOFTER_TEXTURE: 'softer_texture',
} as const;

export const DIET_TYPES = {
    LOW_SODIUM: 'low_sodium',
    BABY_FOOD: 'baby_food',
    DIET: 'diet',
    HIGH_PROTEIN: 'high_protein',
    VEGETARIAN: 'vegetarian',
    LOW_SUGAR: 'low_sugar',
    SOFT_TEXTURE: 'soft_texture',
    QUICK_COOK: 'quick_cook',
} as const;

export const RECIPE_SORTS = {
    VIEW_COUNT: 'view_count',
    LATEST: 'latest',
    POPULAR: 'popular',
    DIFFICULTY: 'difficulty',
    COOKING_TIME: 'cooking_time',
    AI_MODIFIED: 'ai_modified',
} as const;

export const DEFAULT_CATEGORIES = [
    '일반',
    '저염',
    '이유식',
    '다이어트',
    '고단백',
    '반찬',
    '국/찌개',
    '죽/미음',
] as const;

export const DEFAULT_TAGS = [
    '저염',
    '이유식',
    '고단백',
    '다이어트',
    '간단요리',
    '부드러운 식감',
] as const;

export const STATUS_LABELS: Record<string, { labelEn: string; labelKo: string }> = {
    guest: { labelEn: 'Guest', labelKo: '비로그인' },
    user: { labelEn: 'User', labelKo: '일반 사용자' },
    admin: { labelEn: 'Admin', labelKo: '관리자' },
    active: { labelEn: 'Active', labelKo: '정상' },
    suspended: { labelEn: 'Suspended', labelKo: '정지' },
    deleted: { labelEn: 'Deleted', labelKo: '삭제' },
    pending: { labelEn: 'Pending', labelKo: '대기' },
    draft: { labelEn: 'Draft', labelKo: '초안' },
    crawled: { labelEn: 'Crawled', labelKo: '수집 완료' },
    ai_parsed: { labelEn: 'AI Parsed', labelKo: 'AI 정리 완료' },
    ai_modified: { labelEn: 'AI Modified', labelKo: 'AI 개량' },
    pending_review: { labelEn: 'Pending Review', labelKo: '검수 대기' },
    approved: { labelEn: 'Approved', labelKo: '승인' },
    rejected: { labelEn: 'Rejected', labelKo: '반려' },
    hidden: { labelEn: 'Hidden', labelKo: '숨김' },
    queued: { labelEn: 'Queued', labelKo: '대기열' },
    processing: { labelEn: 'Processing', labelKo: '처리 중' },
    completed: { labelEn: 'Completed', labelKo: '완료' },
    failed: { labelEn: 'Failed', labelKo: '실패' },
    visible: { labelEn: 'Visible', labelKo: '공개' },
    reported: { labelEn: 'Reported', labelKo: '신고됨' },
    in_review: { labelEn: 'In Review', labelKo: '검토 중' },
    resolved: { labelEn: 'Resolved', labelKo: '처리 완료' },
    actioned: { labelEn: 'Actioned', labelKo: '조치 완료' },
    error: { labelEn: 'Error', labelKo: '오류' },
    measurement_issue: { labelEn: 'Measurement Issue', labelKo: '계량 문제' },
    source_issue: { labelEn: 'Source Issue', labelKo: '출처 문제' },
    taste_improvement: { labelEn: 'Taste Improvement', labelKo: '맛 개선 요청' },
    other: { labelEn: 'Other', labelKo: '기타' },
    comment: { labelEn: 'Comment', labelKo: '댓글' },
    recipe_version: { labelEn: 'Recipe Version', labelKo: '레시피 버전' },
    recipe_dish: { labelEn: 'Recipe Dish', labelKo: '레시피' },
    spam: { labelEn: 'Spam', labelKo: '스팸' },
    inappropriate: { labelEn: 'Inappropriate', labelKo: '부적절함' },
    wrong_info: { labelEn: 'Wrong Info', labelKo: '잘못된 정보' },
    safety_issue: { labelEn: 'Safety Issue', labelKo: '안전 문제' },
    copyright: { labelEn: 'Copyright', labelKo: '저작권' },
    allowed: { labelEn: 'Allowed', labelKo: '허용' },
    blocked: { labelEn: 'Blocked', labelKo: '차단' },
    collected: { labelEn: 'Collected', labelKo: '수집됨' },
    summarized: { labelEn: 'Summarized', labelKo: '요약됨' },
    expired: { labelEn: 'Expired', labelKo: '만료' },
};

export const PUBLIC_RECIPE_STATUS = RECIPE_STATUSES.APPROVED;
export const REVIEW_REQUIRED_STATUSES = [
    RECIPE_STATUSES.CRAWLED,
    RECIPE_STATUSES.AI_PARSED,
    RECIPE_STATUSES.AI_MODIFIED,
    RECIPE_STATUSES.PENDING_REVIEW,
] as const;

export const SENSITIVE_PROFILE_FIELDS = [
    'allergies',
    'babyAgeMonth',
    'dislikedIngredients',
    'preferredDietTypes',
    'sodiumPreference',
    'texturePreference',
] as const;

export const PAGINATION = {
    DEFAULT_PAGE: 1,
    DEFAULT_DUMP: 20,
    MAX_DUMP: 100,
} as const;

export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];
export type UserStatus = typeof USER_STATUSES[keyof typeof USER_STATUSES];
export type RecipeStatus = typeof RECIPE_STATUSES[keyof typeof RECIPE_STATUSES];
export type AIStatus = typeof AI_STATUSES[keyof typeof AI_STATUSES];
export type AIProcessingStatus = typeof AI_PROCESSING_STATUSES[keyof typeof AI_PROCESSING_STATUSES];
export type AIPromptType = typeof AI_PROMPT_TYPES[keyof typeof AI_PROMPT_TYPES];
export type SourceType = typeof SOURCE_TYPES[keyof typeof SOURCE_TYPES];
export type CommentStatus = typeof COMMENT_STATUSES[keyof typeof COMMENT_STATUSES];
export type EditRequestStatus = typeof EDIT_REQUEST_STATUSES[keyof typeof EDIT_REQUEST_STATUSES];
export type EditRequestType = typeof EDIT_REQUEST_TYPES[keyof typeof EDIT_REQUEST_TYPES];
export type ReportStatus = typeof REPORT_STATUSES[keyof typeof REPORT_STATUSES];
export type ReportTargetType = typeof REPORT_TARGET_TYPES[keyof typeof REPORT_TARGET_TYPES];
export type ReportReason = typeof REPORT_REASONS[keyof typeof REPORT_REASONS];
export type CrawlingStatus = typeof CRAWLING_STATUSES[keyof typeof CRAWLING_STATUSES];
