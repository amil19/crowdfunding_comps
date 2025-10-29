import polars as pl

class Configs:
    embedding_columns = ['creator_name','blurb','name']

    boolean_columns = ['prelaunch_activated']

    categorical = ['country','current_currency','category_name','category_parent_name', 'creator_name']

    numeric_columns = ['goal']

    date_columns = ['launched_at']

    ordinal_columns = ['month','quarter']

    data_struct_schema = pl.Struct([
        pl.Field('spotlight', pl.Boolean),
        pl.Field('usd_pledged', pl.String),
        pl.Field('currency_symbol', pl.String),
        pl.Field('source_url', pl.String),
        pl.Field('current_currency', pl.String),
        pl.Field('currency', pl.String),
        pl.Field('photo', pl.Struct([
            pl.Field('key', pl.String),
            pl.Field('full', pl.String),
            pl.Field('ed', pl.String),
            pl.Field('med', pl.String),
            pl.Field('little', pl.String),
            pl.Field('small', pl.String),
            pl.Field('thumb', pl.String),
            pl.Field('1024x576', pl.String),
            pl.Field('1536x864', pl.String)
        ])),
        pl.Field('backers_count', pl.Int64),
        pl.Field('pledged', pl.Float64),
        pl.Field('slug', pl.String),
        pl.Field('created_at', pl.Int64),
        pl.Field('is_starrable', pl.Boolean),
        pl.Field('static_usd_rate', pl.Float64),
        pl.Field('state', pl.String),
        pl.Field('disable_communication', pl.Boolean),
        pl.Field('fx_rate', pl.Float64),
        pl.Field('creator', pl.Struct([
            pl.Field('id', pl.Int64),
            pl.Field('name', pl.String),
            pl.Field('slug', pl.String),
            pl.Field('is_registered', pl.Null),
            pl.Field('is_email_verified', pl.Null),
            pl.Field('chosen_currency', pl.Null),
            pl.Field('is_superbacker', pl.Null),
            pl.Field('has_admin_message_badge', pl.Boolean),
            pl.Field('ppo_has_action', pl.Boolean),
            pl.Field('backing_action_count', pl.Int64),
            pl.Field('avatar', pl.Struct([
                pl.Field('thumb', pl.String),
                pl.Field('small', pl.String),
                pl.Field('medium', pl.String)
            ])),
            pl.Field('urls', pl.Struct([
                pl.Field('web', pl.Struct([
                    pl.Field('user', pl.String)
                ])),
                pl.Field('api', pl.Struct([
                    pl.Field('user', pl.String)
                ]))
            ]))
        ])),
        pl.Field('video', pl.Struct([
            pl.Field('id', pl.Int64),
            pl.Field('status', pl.String),
            pl.Field('hls', pl.String),
            pl.Field('hls_type', pl.String),
            pl.Field('high', pl.String),
            pl.Field('high_type', pl.String),
            pl.Field('base', pl.String),
            pl.Field('base_type', pl.String),
            pl.Field('tracks', pl.String),
            pl.Field('width', pl.Float32),
            pl.Field('height', pl.Float32),
            pl.Field('frame', pl.String)
        ])),
        pl.Field('profile', pl.Struct([
            pl.Field('id', pl.Int64),
            pl.Field('project_id', pl.Int64),
            pl.Field('state', pl.String),
            pl.Field('state_changed_at', pl.Int64),
            pl.Field('name', pl.String),
            pl.Field('blurb', pl.String),
            pl.Field('background_color', pl.String),
            pl.Field('text_color', pl.String),
            pl.Field('link_background_color', pl.String),
            pl.Field('link_text_color', pl.String),
            pl.Field('link_text', pl.String),
            pl.Field('link_url', pl.String),
            pl.Field('show_feature_image', pl.Boolean),
            pl.Field('background_image_opacity', pl.Float64),
            pl.Field('background_image_attributes', pl.Struct([
                pl.Field('id', pl.Int64),
                pl.Field('image_urls', pl.Struct([
                    pl.Field('default', pl.String),
                    pl.Field('baseball_card', pl.String)
                ]))
            ])),
            pl.Field('should_show_feature_image_section', pl.Boolean),
            pl.Field('feature_image_attributes', pl.Struct([
                pl.Field('id', pl.Int64),
                pl.Field('image_urls', pl.Struct([
                    pl.Field('default', pl.String),
                    pl.Field('baseball_card', pl.String)
                ]))
            ]))
        ])),
        pl.Field('state_changed_at', pl.Int64),
        pl.Field('is_launched', pl.Boolean),
        pl.Field('usd_type', pl.String),
        pl.Field('is_liked', pl.Boolean),
        pl.Field('percent_funded', pl.Float64),
        pl.Field('country', pl.String),
        pl.Field('launched_at', pl.Int64),
        pl.Field('urls', pl.Struct([
            pl.Field('web', pl.Struct([
                pl.Field('project', pl.String),
                pl.Field('rewards', pl.String)
            ]))
        ])),
        pl.Field('id', pl.Int64),
        pl.Field('name', pl.String),
        pl.Field('deadline', pl.Int64),
        pl.Field('goal', pl.Float32),
        pl.Field('country_displayable_name', pl.String),
        pl.Field('is_in_post_campaign_pledging_phase', pl.Boolean),
        pl.Field('location', pl.Struct([
            pl.Field('id', pl.Int64),
            pl.Field('name', pl.String),
            pl.Field('slug', pl.String),
            pl.Field('short_name', pl.String),
            pl.Field('displayable_name', pl.String),
            pl.Field('localized_name', pl.String),
            pl.Field('country', pl.String),
            pl.Field('state', pl.String),
            pl.Field('type', pl.String),
            pl.Field('is_root', pl.Boolean),
            pl.Field('expanded_country', pl.String),
            pl.Field('urls', pl.Struct([
                pl.Field('web', pl.Struct([
                    pl.Field('discover', pl.String),
                    pl.Field('location', pl.String)
                ])),
                pl.Field('api', pl.Struct([
                    pl.Field('nearby_projects', pl.String)
                ]))
            ]))
        ])),
        pl.Field('prelaunch_activated', pl.Boolean),
        pl.Field('blurb', pl.String),
        pl.Field('usd_exchange_rate', pl.Float64),
        pl.Field('category', pl.Struct([
            pl.Field('id', pl.Int64),
            pl.Field('name', pl.String),
            pl.Field('analytics_name', pl.String),
            pl.Field('slug', pl.String),
            pl.Field('position', pl.Float32),
            pl.Field('parent_id', pl.Int64),
            pl.Field('parent_name', pl.String),
            pl.Field('color', pl.Int64),
            pl.Field('urls', pl.Struct([
                pl.Field('web', pl.Struct([
                    pl.Field('discover', pl.String)
                ]))
            ]))
        ])),
        pl.Field('currency_trailing_code', pl.Boolean),
        pl.Field('is_disliked', pl.Boolean),
        pl.Field('staff_pick', pl.Boolean),
        # *** MODIFIED TYPE TO FIX ERROR ***
        pl.Field('converted_pledged_amount', pl.Float32) 
    ])
    # 2. Define the top-level schema
    json_schema = {
        'table_id': pl.String,
        'robot_id': pl.String,
        'run_id': pl.String,
        'data': data_struct_schema, # Use the modified struct schema
    }