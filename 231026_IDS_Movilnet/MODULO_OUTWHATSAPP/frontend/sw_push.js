/**
 * Service Worker Soberano con Soporte de Web Push Notifications (OUTWHATSAPP).
 * Movilnet C.A. — Core PWA 4GMAX.
 * Estrategia: Network-First Zero-Stale + W3C Push API + Notification Click.
 */

const CACHE_NAME = 'movilnet-sovereign-v2';

// 1. Ingesta de Notificación Push en Segundo Plano
self.addEventListener('push', function(event) {
    if (!event.data) {
        console.warn('[SW Push] Evento push recibido sin payload de datos.');
        return;
    }

    let payload = {};
    try {
        payload = event.data.json();
    } catch (e) {
        payload = {
            title: 'Movilnet 4GMAX',
            body: event.data.text(),
            data: { url: '/ui/pwa_stitch/index.html' }
        };
    }

    const options = {
        body: payload.body || 'Tienes una nueva notificación de tu línea Movilnet.',
        icon: payload.icon || '/ui/pwa_stitch/assets/icons/icon-192.png',
        badge: payload.badge || '/ui/pwa_stitch/assets/icons/badge-72.png',
        vibrate: [100, 50, 100],
        data: payload.data || { url: '/ui/pwa_stitch/index.html' },
        actions: [
            { action: 'open', title: '📲 Ver en Portal' },
            { action: 'close', title: 'Cerrar' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(payload.title || 'Movilnet 4GMAX', options)
    );
});

// 2. Manejo de Clic en Notificación (Apertura Soberana)
self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    if (event.action === 'close') {
        return;
    }

    const targetUrl = (event.notification.data && event.notification.data.url) 
        ? event.notification.data.url 
        : '/ui/pwa_stitch/index.html';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if (client.url.includes('/ui/pwa_stitch') && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
