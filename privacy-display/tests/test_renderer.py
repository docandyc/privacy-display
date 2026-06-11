from src.gpu import renderer as renderer_module


def test_create_renderer_falls_back_when_gpu_init_fails(monkeypatch):
    """GPU import 成功但 OpenGL context 创建失败时，应回退到软件渲染器。"""

    def fail_init(self):
        raise RuntimeError("cannot choose pixel format")

    monkeypatch.setattr(renderer_module.GPURenderer, "_init_gl", fail_init)

    renderer = renderer_module.create_renderer(16, 16, 4, gamma=1.0)

    assert isinstance(renderer, renderer_module.SoftwareRenderer)
