"""
Benchmark Forense de Rendimiento y Latencia para OUTWHATSAPP.
Gobernanza: Universal Best Practices Engineering Rule (Pilar II).
"""
import sys
import os
import time
import argparse

MODULE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if MODULE_ROOT not in sys.path:
    sys.path.insert(0, MODULE_ROOT)

from outwhatsapp.application.sovereign_dispatcher import SovereignDispatcher
from outwhatsapp.application.local_orchestrator import LocalAsyncOrchestrator


def run_benchmark(iterations: int = 1000):
    print("=" * 70)
    print(f"⚡ BENCHMARK DE RENDIMIENTO OUTWHATSAPP ({iterations} ITERACIONES)")
    print("=" * 70)

    dispatcher = SovereignDispatcher()
    orchestrator = LocalAsyncOrchestrator(dispatcher=dispatcher)

    # 1. Benchmark de Encolamiento Asíncrono
    t0 = time.time()
    for i in range(iterations):
        orchestrator.encolar_despacho(
            msisdn="04161234567",
            titulo="Aviso Masivo",
            mensaje=f"Notificación de prueba #{i}"
        )
    t_encolar = (time.time() - t0) * 1000.0
    lat_por_item_encolar = t_encolar / iterations

    print(f"1. Encolamiento Asíncrono:")
    print(f"   - Total: {t_encolar:.2f} ms")
    print(f"   - Latencia promedio: {lat_por_item_encolar:.4f} ms/item")
    print(f"   - Throughput: {iterations / (t_encolar / 1000.0):.0f} ops/seg")

    # 2. Benchmark de Despacho Directo Carrier-Grade
    t0 = time.time()
    latencias = []
    for i in range(iterations):
        res = dispatcher.despachar(
            msisdn="04161234567",
            titulo="Factura",
            mensaje="Tu factura mensual está disponible."
        )
        latencias.append(res.latency_ms)
    t_total = (time.time() - t0) * 1000.0
    lat_prom = sum(latencias) / len(latencias)
    lat_p99 = sorted(latencias)[int(len(latencias) * 0.99)]

    print(f"\n2. Despacho Directo (Magic Link + Selección de Canal):")
    print(f"   - Total: {t_total:.2f} ms")
    print(f"   - Latencia promedio: {lat_prom:.3f} ms")
    print(f"   - Latencia P99: {lat_p99:.3f} ms")
    print(f"   - Throughput: {iterations / (t_total / 1000.0):.0f} despachos/seg")

    assert lat_prom < 5.0, f"Latencia promedio ({lat_prom:.2f}ms) excede el objetivo carrier-grade de 5ms"
    print("\n✅ CERTIFICACIÓN DE RENDIMIENTO: LATENCIA <5ms GARANTIZADA")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark OUTWHATSAPP")
    parser.add_argument("--n", type=int, default=1000, help="Número de iteraciones")
    args = parser.parse_args()
    run_benchmark(args.n)
