from h2o_wave import ui


def get_zones():
    return [
        ui.zone(
            name="wrapper",
            size="100vh",
            zones=[
                ui.zone("header", size="100px"),
                ui.zone(
                    "container",
                    # size="1",
                    size="calc(100% - 100px)",
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone(
                            "left_nav", size="250px", direction=ui.ZoneDirection.COLUMN
                        ),
                        ui.zone(
                            "main_content",
                            size="",
                            direction=ui.ZoneDirection.COLUMN,
                            zones=[
                                ui.zone(
                                    "main_top",
                                    size="calc(100% - 275px)",
                                    direction=ui.ZoneDirection.ROW,
                                    justify="around",
                                    zones=[
                                        ui.zone(
                                            "model_left",
                                            # size="48%",
                                            size="calc((100% - 220px) / 2)",
                                        ),
                                        ui.zone(
                                            "actions",
                                            # size="4%",
                                            size="220px",
                                        ),
                                        ui.zone(
                                            "model_right",
                                            # size="48%",
                                            size="calc((100% - 220px) / 2)",
                                        ),
                                    ],
                                ),
                                ui.zone(
                                    "main",
                                    size="200px",
                                    direction=ui.ZoneDirection.COLUMN,
                                ),
                                ui.zone(
                                    name="footer",
                                    size="65px",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]


def get_zones2():
    return [
        ui.zone(
            name="wrapper",
            size="100vh",
            zones=[
                ui.zone("header", size="100px"),
                ui.zone(
                    "container",
                    size="calc(100% - 170px)",
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone(
                            "left_nav",
                            size="250px",
                            direction=ui.ZoneDirection.COLUMN,
                        ),
                        ui.zone(
                            "main_content",
                            direction=ui.ZoneDirection.COLUMN,
                            size="calc(100% - 255px)",
                            zones=[
                                ui.zone(
                                    "main",
                                    size="150px",
                                    direction=ui.ZoneDirection.COLUMN,
                                ),
                                ui.zone(
                                    "main_top",
                                    size="calc(100% - 150px)",
                                    direction=ui.ZoneDirection.ROW,
                                    justify="around",
                                    zones=[
                                        ui.zone(
                                            "model_left",
                                            size="calc((100% - 220px) / 2)",
                                        ),
                                        ui.zone(
                                            "actions",
                                            size="220px",
                                        ),
                                        ui.zone(
                                            "model_right",
                                            size="calc((100% - 220px) / 2)",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                ui.zone(
                    name="footer",
                    size="65px",
                ),
            ],
        ),
    ]


def get_zones3():
    return [
        ui.zone(
            name="wrapper",
            size="100vh",
            zones=[
                ui.zone("header", size="100px"),
                ui.zone(
                    "container",
                    size="calc(100% - 105px)",
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone(
                            "left_nav",
                            size="250px",
                            direction=ui.ZoneDirection.COLUMN,
                        ),
                        ui.zone(
                            "main_content",
                            direction=ui.ZoneDirection.COLUMN,
                            zones=[
                                ui.zone(
                                    "main",
                                    size="150px",
                                    direction=ui.ZoneDirection.COLUMN,
                                ),
                                ui.zone(
                                    "main_1",
                                    size="150px",
                                    direction=ui.ZoneDirection.COLUMN,
                                ),
                                ui.zone(
                                    "main_top",
                                    size="calc(100% - 215px)",
                                    direction=ui.ZoneDirection.ROW,
                                    justify="around",
                                    zones=[
                                        ui.zone(
                                            "model_left",
                                            size="calc((100% - 220px) / 2)",
                                        ),
                                        ui.zone(
                                            "actions",
                                            size="220px",
                                        ),
                                        ui.zone(
                                            "model_right",
                                            size="calc((100% - 220px) / 2)",
                                        ),
                                    ],
                                ),
                                ui.zone(
                                    name="footer",
                                    size="65px",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]


def get_zones1():
    return [
        ui.zone(
            name="wrapper",
            size="100vh",
            zones=[
                ui.zone(
                    "wrapper1",
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone(
                            "left_nav",
                            size="250px",
                            direction=ui.ZoneDirection.COLUMN,
                        ),
                        ui.zone(
                            "main_content",
                            zones=[
                                ui.zone(
                                    "main",
                                    size="1",
                                    direction=ui.ZoneDirection.COLUMN,
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
    ]


def get_zones4(model_rows=10):
    model_zones = [
        ui.zone(
            f"model_row_{i}",
            direction=ui.ZoneDirection.ROW,
        )
        for i in range(model_rows)
    ]

    return [
        ui.zone(
            name="wrapper",
            size="100vh",
            zones=[
                ui.zone("header", size="100px"),
                ui.zone(
                    "container",
                    size="calc(100% - 170px)",
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone(
                            "left_nav",
                            size="250px",
                            direction=ui.ZoneDirection.COLUMN,
                        ),
                        ui.zone(
                            "main_content",
                            direction=ui.ZoneDirection.COLUMN,
                            size="calc(100% - 255px)",
                            zones=[
                                ui.zone(
                                    "main",
                                    direction=ui.ZoneDirection.COLUMN,
                                ),
                                ui.zone(
                                    "gpt_evals",
                                    direction=ui.ZoneDirection.COLUMN,
                                ),
                            ]
                            + model_zones,
                        ),
                    ],
                ),
            ],
        ),
    ]


def get_layouts():
    layouts = [
        ui.layout(
            breakpoint="xs",
            min_height="100vh",
            zones=get_zones2(),
        ),
    ]
    return layouts
