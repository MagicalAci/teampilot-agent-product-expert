import SwiftUI

struct ContentView: View {
    var body: some View {
        ZStack {
            DemoTokens.background.ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("[DEMO_TITLE]")
                        .font(.system(size: 34, weight: .bold))
                        .foregroundStyle(DemoTokens.text)

                    Text("这是一个 SwiftUI demo 骨架。建议先让首屏讲清价值，再补关键路径和状态页。")
                        .font(.body)
                        .foregroundStyle(DemoTokens.subtleText)

                    VStack(spacing: 14) {
                        DemoCard(title: "核心路径", body: "展示用户从进入到完成动作的第一条主链路。")
                        DemoCard(title: "关键状态", body: "展示结果反馈、数据变化或体验亮点。")
                        DemoCard(title: "交接提示", body: "说明哪些素材、接口或状态还是占位。")
                    }

                    Button("开始演示") {
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(DemoTokens.primary)
                }
                .padding(24)
            }
        }
    }
}

private struct DemoCard: View {
    let title: String
    let body: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundStyle(DemoTokens.text)
            Text(body)
                .font(.subheadline)
                .foregroundStyle(DemoTokens.subtleText)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(DemoTokens.surface)
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

#Preview {
    ContentView()
}
