#!/usr/bin/env python3
"""
AI前沿技术进展追踪系统主程序
每天自动生成AI技术进展PDF报告
"""


from src.processors.pdf_generator import PDFGenerator
from src.processors.paper_summarizer import PaperSummarizer
from src.crawlers.arxiv_crawler import ArxivCrawler
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 确保 data 目录存在（日志文件需要）
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)


class AITracker:
    def __init__(self):
        """初始化AI追踪系统"""
        self.crawler = ArxivCrawler()
        self.summarizer = PaperSummarizer()
        self.pdf_generator = PDFGenerator()
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def run_daily_report(self, days: int = 1, max_papers: int = 30):
        """
        运行每日报告生成

        Args:
            days: 搜索最近几天的论文
            max_papers: 最大论文数量
        """
        logging.info("开始生成AI技术进展日报...")

        try:
            # 1. 爬取最新论文
            logging.info("正在爬取arXiv最新论文...")
            papers = self.crawler.search_recent_papers(
                days=days, max_results=max_papers)
            logging.info(f"成功获取 {len(papers)} 篇论文")

            if not papers:
                logging.warning("未找到任何论文，生成空报告")
                self._generate_empty_report()
                return

            # 2. 生成论文摘要
            logging.info("正在生成论文摘要...")
            summarized_papers = self.summarizer.generate_batch_summaries(
                papers[:max_papers])
            logging.info("摘要生成完成")

            # 3. 生成PDF报告
            logging.info("正在生成PDF报告...")
            pdf_path = self.pdf_generator.generate_daily_report(
                summarized_papers)
            logging.info(f"PDF报告已生成: {pdf_path}")

            # 4. 保存数据
            self._save_data(summarized_papers)

            logging.info("日报生成完成!")
            self._print_summary(summarized_papers)

        except Exception as e:
            logging.error(f"生成日报时发生错误: {e}")
            raise

    def run_simple_report(self, days: int = 1, max_papers: int = 50):
        """
        运行简化版报告生成（不含AI摘要）

        Args:
            days: 搜索最近几天的论文
            max_papers: 最大论文数量
        """
        logging.info("开始生成简化版AI技术进展报告...")

        try:
            # 爬取论文
            papers = self.crawler.search_recent_papers(
                days=days, max_results=max_papers)
            logging.info(f"获取到 {len(papers)} 篇论文")

            # 生成简化版PDF
            pdf_path = self.pdf_generator.generate_simple_report(papers)
            logging.info(f"简化版PDF报告已生成: {pdf_path}")

        except Exception as e:
            logging.error(f"生成简化版报告时发生错误: {e}")
            raise

    def _generate_empty_report(self):
        """生成空报告"""
        empty_papers = []
        pdf_path = self.pdf_generator.generate_daily_report(empty_papers)
        logging.info(f"空报告已生成: {pdf_path}")

    def _save_data(self, papers: list):
        """保存论文数据"""
        import json
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_file = self.data_dir / f"papers_{timestamp}.json"

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)

        logging.info(f"论文数据已保存到: {data_file}")

    def _print_summary(self, papers: list):
        """打印摘要信息"""
        print("\n" + "="*60)
        print("AI技术进展日报摘要")
        print("="*60)

        # 统计分类
        categories = {}
        for paper in papers:
            category = self._get_paper_category(paper)
            categories[category] = categories.get(category, 0) + 1

        print(f"总计论文数: {len(papers)}")
        print("分类统计:")
        for category, count in categories.items():
            print(f"  {category}: {count}篇")

        print("\n前5篇论文:")
        for i, paper in enumerate(papers[:5]):
            print(f"{i+1}. {paper['title'][:60]}...")
            if paper.get('ai_summary'):
                print(f"   {paper['ai_summary']}")

        print("="*60)

    def _get_paper_category(self, paper):
        """获取论文分类"""
        categories = paper.get('categories', [])
        if any('cs.CV' in cat for cat in categories):
            return '计算机视觉'
        elif any('cs.CL' in cat for cat in categories):
            return '自然语言处理'
        elif any('cs.LG' in cat or 'stat.ML' in cat for cat in categories):
            return '机器学习'
        else:
            return '其他'


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AI前沿技术进展追踪系统')
    parser.add_argument('--mode', choices=['daily', 'simple'], default='daily',
                        help='报告模式: daily(完整报告) 或 simple(简化报告)')
    parser.add_argument('--days', type=int, default=1,
                        help='搜索最近几天的论文')
    parser.add_argument('--max-papers', type=int, default=30,
                        help='最大论文数量')

    args = parser.parse_args()

    tracker = AITracker()

    try:
        if args.mode == 'daily':
            tracker.run_daily_report(
                days=args.days, max_papers=args.max_papers)
        else:
            tracker.run_simple_report(
                days=args.days, max_papers=args.max_papers)

    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
