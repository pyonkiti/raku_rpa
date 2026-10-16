import yaml
import common.config    as config
from pathlib            import Path

# --------------------------------------------------------------------
# 共通処理
# --------------------------------------------------------------------
class COMMON:

    # --------------------------------------------------------------------
    # YAMLファイルの読み込み
    # --------------------------------------------------------------------
    def get_yaml(self):

        if not Path(config.path_yml).exists():
            return "yamlファイルが存在しません。"
        
        with open(Path(config.path_yml), mode = "r", encoding = "utf-8") as f:
            system = yaml.safe_load(f)

        config.rakuraku["id"] = system["rakuraku"]["id"]                                # ID
        config.rakuraku["pw"] = system["rakuraku"]["pw"]                                # pw

        return None
 
    # --------------------------------------------------------------------
    # ログの出力
    # --------------------------------------------------------------------
    def log_exception(self, e: Exception, show_locals: bool = True) -> str:

        lines = []
        lines.append(f"例外クラス : {type(e).__module__}.{type(e).__qualname__}")
        lines.append(f"メッセージ : {e}")
        lines.append("-" * 70)
        lines.append("呼び出し経路:")

        tb = e.__traceback__
        depth = 0
        last_frame_info = None
        while tb:
            frame = tb.tb_frame
            code = frame.f_code
            qualname = getattr(code, "co_qualname", code.co_name)
            filename = code.co_filename
            lineno = tb.tb_lineno

            try:
                with open(filename, encoding="utf-8") as f:
                    source_line = f.readlines()[lineno - 1].strip()
            except Exception:
                source_line = "(ソース取得不可)"

            lines.append(f"  [{depth}] {qualname}  ({filename}:{lineno})")
            lines.append(f"       >> {source_line}")

            if show_locals:
                for k, v in frame.f_locals.items():
                    if k in ("self", "cls"):
                        continue
                    try:
                        v_repr = repr(v)
                    except Exception:
                        v_repr = "<repr失敗>"
                    if len(v_repr) > 200:
                        v_repr = v_repr[:200] + "...(省略)"
                    lines.append(f"         {k} = {v_repr}")

            last_frame_info = (qualname, filename, lineno)
            depth += 1
            tb = tb.tb_next

        lines.append("-" * 70)
        if last_frame_info:
            qualname, filename, lineno = last_frame_info
            lines.append(f" 発生箇所: {qualname}  ({filename}:{lineno})")

        if e.__cause__:
            lines.append("-" * 70)
            lines.append(" 直接の原因となった例外（raise ... from ...）:")
            lines.append(f"   {type(e.__cause__).__name__}: {e.__cause__}")
        elif e.__context__ and e.__context__ is not e:
            lines.append("-" * 70)
            lines.append(" 処理中に暗黙的に発生していた元の例外:")
            lines.append(f"   {type(e.__context__).__name__}: {e.__context__}")

        return "\n".join(lines)
