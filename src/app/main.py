"""
Main entry point for the stock research application with Flask UI.
Located in src/app/main.py
"""
import json
import uuid
import logging
import os
import subprocess
from typing import List, Dict, Any
from datetime import datetime

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import markdown2

# Configure logging first so it's available for import attempts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from src.core.agent.graph import create_research_graph
    logger.info("Successfully imported create_research_graph from src.core.agent.graph")
except ImportError as e_main:
    logger.error(f"Initial ImportError for src.core.agent.graph: {e_main}")
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"Added project root to sys.path: {project_root}")
    try:
        from src.core.agent.graph import create_research_graph
        logger.info("Successfully imported create_research_graph after sys.path modification.")
    except ImportError as e_fallback:
        logger.error(f"Fallback ImportError for src.core.agent.graph: {e_fallback}", exc_info=True)
        raise

# Flask app initialization
app = Flask(__name__, template_folder='templates', static_folder='static') 
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super_secret_key_for_dev_only")

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'reports'))
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)
    logger.info(f"Created reports directory: {REPORTS_DIR}")

def run_stock_research(stocks: List[str], topic: str = "Brazilian Stock Research") -> Dict[str, Any]:
    logger.info(f"Starting research on: {topic}")
    logger.info(f"Stocks to be analyzed: {', '.join(stocks)}")
    try:
        research_graph = create_research_graph()
        thread_id = str(uuid.uuid4())
        thread = {"configurable": {"thread_id": thread_id}}
        logger.info(f"Thread ID: {thread_id}")
        state = {"topic": topic, "stocks": stocks}
        logger.info("Starting research graph execution...")
        for event in research_graph.stream(state, thread, stream_mode="values"):
            analysts = event.get('analysts', [])
            if analysts:
                logger.info(f"Generated {len(analysts)} analysts.")
        logger.info("Continuing execution to generate the report...")
        for event in research_graph.stream(None, thread, stream_mode="update"):
            node_name = next(iter(event.keys()), None)
            if node_name:
                logger.info(f"Executing node: {node_name}")
        final_state = research_graph.get_state(thread)
        logger.info("Research completed successfully!")
        return final_state.values
    except Exception as e:
        logger.error(f"Error during stock research: {e}", exc_info=True)
        return None

def save_report_for_download(report_content: str) -> str | None:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4()).split('-')[0]
        filename = f"stock_report_{timestamp}_{short_uuid}.md"
        filepath = os.path.join(REPORTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Report saved to: {filepath}")
        return filename
    except Exception as e:
        logger.error(f"Error saving report for download: {e}", exc_info=True)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    report_html = None
    report_filename = None
    error_message = None
    processing_message = None
    if request.method == 'POST':
        stocks_input = request.form.get('stocks', '').strip()
        if not stocks_input:
            error_message = "Please enter at least one stock symbol."
            return render_template('index.html', error_message=error_message, request=request)
        stocks = [s.strip().upper() for s in stocks_input.replace('\n', ',').split(',') if s.strip()]
        if not stocks:
            error_message = "No valid stock symbols were provided after processing."
            return render_template('index.html', error_message=error_message, request=request)
        logger.info(f"Received stock symbols for research: {stocks}")        
        processing_message = f"Processing report for stocks: {', '.join(stocks)}. This may take a few minutes..."
        results = run_stock_research(stocks)
        if results and "final_report" in results:
            report_md = results["final_report"]
            try:
                report_html = markdown2.markdown(report_md, extras=["tables", "fenced-code-blocks", "code-friendly"])
            except Exception as e:
                logger.error(f"Error converting Markdown to HTML: {e}")
                error_message = "Error converting report for display."
                report_html = f"<p>Error rendering report: {e}</p><pre>{report_md}</pre>"
            report_filename = save_report_for_download(report_md)
            if not report_filename:
                flash("Error saving the report file for download.", "error")
        elif results is None:
            error_message = "An internal error occurred while generating the report. Please check the logs for more details."
        else:
            error_message = "No report was generated. Please check the stock symbols and try again."
            logger.warning(f"No report generated for stocks: {stocks}. Results: {results}")
    return render_template('index.html', 
                           report_html=report_html, 
                           report_filename=report_filename, 
                           error_message=error_message,
                           processing_message=processing_message,
                           request=request)

@app.route('/download/<filename>')
def download_report(filename):
    logger.info(f"Attempting to download report: {filename} from {REPORTS_DIR}")
    try:
        return send_from_directory(REPORTS_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        logger.error(f"File not found for download: {filename} in {REPORTS_DIR}")
        flash("Report file not found.", "error")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error during file download: {e}", exc_info=True)
        flash("Error downloading the report file.", "error")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)

