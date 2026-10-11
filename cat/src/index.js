// Cat（猫影视 / MiraPlay / HawkPlayer）源入口，结构参照 CatPawOpen。
import { createServer } from 'http';
import Fastify from 'fastify';
import router from './router.js';

let server = null;

export async function start(config) {
    server = Fastify({
        serverFactory: (handler) => createServer((req, res) => handler(req, res)),
        forceCloseConnections: true,
        logger: false,
        maxParamLength: 10240,
    });
    server.address = function () {
        const result = this.server.address();
        result.url = `http://${result.address}:${result.port}`;
        result.dynamic = 'js2p://_WEB_';
        return result;
    };
    server.stop = false;
    server.config = config || {};
    server.register(router);
    await server.listen({ port: Number(process.env.DEV_HTTP_PORT) || 0, host: '127.0.0.1' });
    return server;
}

export async function stop() {
    if (server) {
        server.stop = true;
        await server.close();
    }
    server = null;
}
