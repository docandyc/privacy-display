#version 330 core

uniform sampler2D u_image;    // 原始图像纹理
uniform sampler2D u_mask;     // 二值掩模纹理（R8_UINT 语义，值 0 或 1）
uniform sampler2D u_noise;    // 子噪声纹理（RGBA float，已缩放到 [0,1] 空间）
uniform float u_gamma;        // 亮度补偿系数
uniform bool u_inversion;     // 是否输出反色帧

in vec2 v_texcoord;
out vec4 frag_color;

void main() {
    vec4 pixel   = texture(u_image, v_texcoord);
    float mask   = texture(u_mask,  v_texcoord).r;  // 0.0 or 1.0
    vec4 noise   = texture(u_noise, v_texcoord) - 0.5; // 反中心化：[0,1]→[-0.5,0.5]

    // 子帧基础值：I_k = I * M_k + N_k
    // 注意：噪声必须全帧注入（不乘掩模），否则每像素仅在激活时隙
    // 收到一次噪声，时域互补消除约束 ΣN_k=0 被破坏
    vec4 subframe = pixel * mask + noise;

    // 亮度补偿：I_k_comp = clip(I_k * gamma, 0, 1)
    vec4 compensated = clamp(subframe * u_gamma, 0.0, 1.0);

    // 反色帧（长曝光防御）
    if (u_inversion) {
        frag_color = vec4(1.0) - compensated;
        frag_color.a = 1.0;
    } else {
        frag_color = vec4(compensated.rgb, 1.0);
    }
}
