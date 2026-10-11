import sites from '../sites.json';
import cms from './cms.js';

const PREFIX = '/spider';

export default async function router(fastify) {
    for (const site of sites) {
        fastify.register(cms(site), { prefix: `${PREFIX}/${site.key}/3` });
    }
    fastify.get('/check', async () => ({ run: !fastify.stop }));
    fastify.get('/config', async () => ({
        video: {
            sites: sites.map((s) => ({
                key: 'nodejs_' + s.key,
                name: s.name,
                type: 3,
                api: `${PREFIX}/${s.key}/3`,
            })),
        },
        read: { sites: [] },
        comic: { sites: [] },
        music: { sites: [] },
        pan: { sites: [] },
        color: fastify.config.color || [],
    }));
}
