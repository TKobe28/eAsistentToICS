from getter import get_weeks
from datetime import date
from ics import Calendar, Event
from collections import defaultdict
from models import  *

if __name__ == "__main__":
    session_key = "v1.oavmruVYOo4g-d6tdCXDpjGJ14pD3-XLprzA-FHJGLQLQ7UQrVN2qZ8Nw0_IV2sj7m9MsZMiNHbP25kJtq7JFVxBqapbg1OZhYD-vuCRTVRKD35OVsLxGkktDfhaPbrlTeHIzd4YWTFSfLf-vQd2_X1nDcrOHd2DtF8ssegVBlJgEq2JzNtNnXjjHzHGxNvhRY7MHdJ20vR3ZahoiiqAnDeg18OL9W_g0zXlHerTiJvGKdFiAtQwkDJ_PFIGcGmStzZ3uUsu_GV_9dxLLo6Rp8aGzOYsA8K7ZLaM1NsF7P_bWXk37Tgbz-7-YkOaMDjbmhVEn4nkN2UwovWBEVyAPpLaNHNMnslsBpwhzeGIove1J1rBDjH9Qlx-TqvKFca17OKmE15sFg826x0SEgjXvRD0IZ0M2msx1UWLr3gc6AMNbqSQ0536fMf9SlNBlwm_psAgjVVKWkUImOviOtgAmvghz_xFnytDzSJ0Arb4IfA6h30DKYIIa7v8ZI_EYiqLSpoDM6BRaAIGnUVtFAeZcai_HHmzNarInYzWxcOXdVHhL8RXI5EXKo8wKIM-cghE9Ub05NUyg3o2htkJW8XJMPLERK3Mtdq_qJM10I5cQ65TjtR3B2kS3_DB8Le97XItRkYpwPV0jIiI5HRucHYGF9TQBbY8iVIyO7DId40hJrwF_dosfkETAd1XgogxcR0XqRgBZpHtq-siNWjfUAWaagqkWhFi7yj7JlCKuDeQl7CvCUBek_5PdRUgKWiU7alMcR9djY3_iAehaIL6KZpbnTdPzoXdGcBr1yRRKK5z-M9oWmnW4IjfeTuc66FLLSjJTyi-TT32akdBRFXOctGm7gdWk3yK81eQ3PpEqE9Jn94rtOsoGfs6W3PDyTj7_FXYkAhWp8knJ_8AZIdUH77CoLHlKZB-neESpZonS8UdUqjEg18z6C-UF_a2dOnNvlyUVtJEZwTzGm5-ru1BWdn71lUxlxK1oXowdUiY9mXMP6vLlk4fAghFnt-u88l5L23Jl4ToWz6C_pIw8bt7FsKX-0sh4JuWmh69M5qcmFi6B_VJgZ_CfmsgiYTxLfFWZV0GQOsmsDBKBzC5RTIasteWy0p-KtdBE9TMC6JP9YLPI0LqtS2_M0wZKF3NE3Q0Y5oli5s6Qkm5MDT64eTrQYE7otaa8LgiLyTSoyUNHhEUR42G1GAXe_eG3bjh1Nb90rVxcs0nPbGRPtHTXJ-N4-gad4IdVrznmEy6FgKCzkG4TzVXJts7oW8EAhju5UdWbx_OYXDpSHnvqhayLBTbNEKTTAE6O4CdeB15pxOHkEQm4ioJRF0K6JIoIdbcSSHy0_sZNTofLmfFWsyzh69VRBmoYfoePVccYc9dNIiBT00pQolvsW0BUXNsFOKIuPZjnLcL8fypu2CbWS5GC28kL7Sc3k8rzULYhz1GvGpUYLPtgfeEaSaahw6IUoqOcY7TIpygLhIfXG3ST5mMZSp1M3w1PucBRkPwihi0JG7Aoqr5rgWButYZQWk0_J7mqN_Nphy3R4_YhtmIzUXAKKVjLc42drZYOqANU3pysLZxpur7Yw4Q497ww-BusSZ4qRsEWoOaWCUfoefUpHD8KyBw_FI3qc8QTCwz5SNKHull2mw8499f2OdtH7jtddCE5YXjE7qHk29tmTC3Q5mPkIAq96rZIx-qhDRQRtaIO6wjmwBWN6nxfZLV2imZTHS3K8gDrgggqgUujbmsD-q_bFR3D4nIcg5AiaGq5aazoIeUa3OXK1-baceH5GZajawJWGwWlTGoVG3odb_KYp79n7_68HCYtobFHKUa8w5fWgwqZ2E1i5ZKyUqMnt42OxiA10gLo7JC88joTgTB3YKLSuslh4GH8VUacMDeQdLJHOuddO19QYOIJ9A6d6ciyd0YbGh3rGQE1PMx_-cjypXbKzjUpHqYe3klhN2Br0GpvUtFHe08q-0N1ADznzvp7II9jDOiz7fnb7AKynlUxR4YH6kKOexi7uQFr62H74wX2YdtZirJi0UUmeqecxzFYRTc4JWWzQMfyE37ORrHLt7KDqE8thzAXhZ7dCaAVJO--pFlgSaRRDE"
    weeks = get_weeks(user="1", session_key=session_key, start=date(2025, 9, 1), end=date(2026, 6, 20), rewrite=False)
    calendar = Calendar()

    num_of_instances = defaultdict(int)
    fields_per_field = defaultdict(set)
    for week in weeks:
        for event in week.events:
            num_of_instances[event.__class__.__name__] += 1
            calendar.events.add(
                event.to_ics(week.schedule)
            )

            if isinstance(event, SchoolHour | SchoolEvent):
                for thing in event.model_extra:
                    fields_per_field[event.__class__.__name__].add(thing)
                if "subject" in event.model_fields and event.subject is not None:
                    for thingy in event.subject.model_extra:
                        fields_per_field["Subject"].add(thingy)
                if "evaluation" in event.model_fields and event.evaluation is not None:
                    for thingy in event.evaluation.model_extra:
                        fields_per_field["Evaluation"].add(thingy)
    print(num_of_instances)
    print(fields_per_field)
    output = "calendar.ics"
    with open(output, "w") as f:
        f.writelines(calendar)
