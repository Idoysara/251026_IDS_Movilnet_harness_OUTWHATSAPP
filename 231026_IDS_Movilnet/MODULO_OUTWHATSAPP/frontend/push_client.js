/**
 * Cliente JavaScript de Registro Web Push y Biometría WebAuthn.
 * Movilnet C.A. — Core PWA OUTWHATSAPP.
 */

class MovilnetPushClient {
    constructor(apiBaseUrl = 'http://localhost:8035/api/v1', vapidPublicKey = null) {
        this.apiBaseUrl = apiBaseUrl;
        this.vapidPublicKey = vapidPublicKey || 'BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjZJuNn0W0_QdnFrnbfRHyED95BKA';
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    async solicitarPermisoYSuscribir(userMsisdn) {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            console.warn('[Web Push] Este navegador no soporta notificaciones push nativas.');
            return { success: false, reason: 'UNSUPPORTED' };
        }

        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            console.warn('[Web Push] Permiso de notificaciones denegado por el usuario.');
            return { success: false, reason: 'DENIED' };
        }

        try {
            const registration = await navigator.serviceWorker.ready;
            const convertedVapidKey = this.urlBase64ToUint8Array(this.vapidPublicKey);

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: convertedVapidKey
            });

            const subJson = subscription.toJSON();
            const payload = {
                endpoint: subJson.endpoint,
                keys: {
                    p256dh: subJson.keys.p256dh,
                    auth: subJson.keys.auth
                },
                user_msisdn: userMsisdn
            };

            const resp = await fetch(`${this.apiBaseUrl}/push/subscribe`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await resp.json();
            return { success: resp.ok, data: result };
        } catch (error) {
            console.error('[Web Push] Error durante la suscripción:', error);
            return { success: false, error: error.message };
        }
    }
}

if (typeof window !== 'undefined') {
    window.MovilnetPushClient = MovilnetPushClient;
}
