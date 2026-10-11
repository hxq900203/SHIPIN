// 苹果CMS（type 1，JSON）采集接口 → Cat 源接口
import axios from 'axios';

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15';

function pick(v) {
    return {
        vod_id: String(v.vod_id),
        vod_name: v.vod_name,
        vod_pic: v.vod_pic,
        vod_remarks: v.vod_remarks || '',
    };
}

export default function cms(site) {
    const get = async (params) => {
        const resp = await axios.get(site.api, { params, headers: { 'User-Agent': UA }, timeout: 15000 });
        return typeof resp.data === 'string' ? JSON.parse(resp.data) : resp.data;
    };

    return async (fastify) => {
        fastify.post('/init', async () => ({}));

        fastify.post('/home', async () => {
            const data = await get({ ac: 'list' });
            const classes = (data.class || []).map((c) => ({ type_id: String(c.type_id), type_name: c.type_name }));
            return { class: classes, filters: {} };
        });

        fastify.post('/category', async (req) => {
            const { id, page } = req.body || {};
            const pg = Number(page) || 1;
            const data = await get({ ac: 'detail', t: id, pg });
            return {
                page: Number(data.page) || pg,
                pagecount: Number(data.pagecount) || 1,
                limit: Number(data.limit) || 20,
                total: Number(data.total) || 0,
                list: (data.list || []).map(pick),
            };
        });

        fastify.post('/detail', async (req) => {
            const id = req.body?.id;
            const ids = Array.isArray(id) ? id.join(',') : id;
            const data = await get({ ac: 'detail', ids });
            return { list: data.list || [] };
        });

        fastify.post('/play', async (req) => {
            const url = req.body?.id || '';
            const direct = /\.(m3u8|mp4|flv)(\?|$)/i.test(url);
            return direct ? { parse: 0, url } : { parse: 1, jx: 1, url };
        });

        fastify.post('/search', async (req) => {
            const { wd, page } = req.body || {};
            const pg = Number(page) || 1;
            const data = await get({ ac: 'detail', wd, pg });
            return {
                page: Number(data.page) || pg,
                pagecount: Number(data.pagecount) || 1,
                list: (data.list || []).map(pick),
            };
        });
    };
}
