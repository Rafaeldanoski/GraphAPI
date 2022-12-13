import requests
import json
import pandas as pd
import copy
import numpy as np


# https://developers.facebook.com/tools/explorer?method=GET&path=act_3120164588217844%2Fadsets%3Ffields%3Dname%2Cstatus%2Cid%2C&version=v13.0

# act_3120164588217844/insights?level=adset&fields=spend,cpc,cpm,objective,adset_name,adset_id,clicks,campaign_name,campaign_id,conversions,frequency,conversion_values,ad_name,ad_id,ad_impression_actions
# act_3120164588217844/campaigns?fields=name,daily_budget,status,adsets{name,id,status},objective,spend_cap,insights.date_preset(last_7d).time_increment(1){cpc, ctr}
#act_3120164588217844/campaigns?fields=name,daily_budget,status,adsets{name,id,status},objective,spend_cap,insights.limit(10){cpc,ctr,dda_results,conversions,converted_product_quantity,account_currency,account_name,account_id,attribution_setting,adset_name,adset_id,buying_type,campaign_id,campaign_name,canvas_avg_view_percent,canvas_avg_view_time,catalog_segment_value,clicks,conversion_rate_ranking,conversion_values,converted_product_value,cost_per_conversion,cost_per_estimated_ad_recallers,cost_per_inline_link_click,cost_per_inline_post_engagement,cost_per_outbound_click,cost_per_thruplay,cost_per_unique_click,cost_per_unique_inline_link_click,cost_per_unique_outbound_click,cpm,cpp,date_start,date_stop,engagement_rate_ranking,estimated_ad_recall_rate,estimated_ad_recallers,frequency,full_view_impressions,full_view_reach,impressions,inline_link_click_ctr,inline_link_clicks,inline_post_engagement,instant_experience_clicks_to_open,instant_experience_clicks_to_start,instant_experience_outbound_clicks,mobile_app_purchase_roas,objective,optimization_goal,outbound_clicks,outbound_clicks_ctr,place_page_name,purchase_roas,qualifying_question_qualify_answer_rate,quality_ranking,reach,social_spend,spend,video_play_actions,video_play_curve_actions,website_ctr,website_purchase_roas,action_values,ad_name,actions,ad_id}
# act_3120164588217844/campaigns?fields=name,daily_budget,status,adsets{name,id,status},objective,spend_cap,insights.limit(10){cpc,ctr,actions, website_purchase_roas, action_values, spend, inline_post_engagement, inline_link_clicks, inline_link_click_ctr, frequency, cost_per_unique_click, clicks, conversions}
#act_3120164588217844/campaigns?fields=name,daily_budget,status,adsets{name,id,status},objective,spend_cap,insights.time_range({since:"2022-08-07",until:"2022-08-14"}){cpc,ctr,actions, website_purchase_roas, spend, inline_post_engagement, inline_link_clicks, inline_link_click_ctr, frequency, cost_per_unique_click, clicks}

# act_3120164588217844/adsets?fields=name,status,id,daily_budget,insights{cpc,ctr,actions,website_purchase_roas,spend,inline_post_engagement,inline_link_clicks,inline_link_click_ctr,frequency,cost_per_unique_click,clicks,video_p25_watched_actions,video_p50_watched_actions,video_p75_watched_actions,reach,impressions,cpm},campaign,campaign_id&limit=10000'

class GraphAPI:
    def __init__(self, ad_acc, fb_api):
        self.ad_acc = ad_acc
        self.base_url = "https://graph.facebook.com/v15.0/"
        self.api_fields = ["spend", "cpc", "cpm", "objective", "adset_name", 
                "adset_id", "clicks", "campaign_name", "campaign_id", 
                "conversions", "frequency", "conversion_values", "ad_name", "ad_id", "purchase_roas"]
        self.token = "&access_token=" + fb_api
        self._set_fields()

    def _set_fields(self):
        self.fields = ['cpc', 'ctr', 'actions', 'spend', 'frequency', 'cost_per_unique_click',
                       'clicks ', 'video_p25_watched_actions', 'video_p50_watched_actions', 'video_p75_watched_actions', 
                       'reach','impressions','cpm', 'purchase_roas', 'conversion_values','inline_link_clicks']
        self.mean_based_fields= ['cpc', 'ctr', 'frequency', 'cost_per_unique_click', 'cpm', 'purchase_roas']

    # ========================================
    # Base requests
    def get_insights(self , ad_acc, level="campaign"):
        url = self.base_url + "act_" + str(ad_acc)
        url += "/insights?level=" + level
        url += "&fields=" + ",".join(self.api_fields)

        data = requests.get(url + self.token)
        data = json.loads(data._content.decode("utf-8"))
        for i in data["data"]:
            if "conversions" in i:
                i["conversion"] = float(i["conversions"][0]["value"])
        return data

    def get_campaigns_status(self, since_until=None, date_preset=None, increment='all_days', process=True):
        url = self.base_url + "act_" + str(self.ad_acc)
        url += "/campaigns?fields=name,status,id, objective, daily_budget, adsets{name, id, status},insights"

        if since_until:
            url += '.time_range({since:"'+ since_until[0] +'", until:"'+ since_until[1] +'"})'
        elif date_preset:
            url+='.date_preset({})'.format(date_preset)
        if increment:
            url+='.time_increment({})'.format(increment)
        
        url += "{"+','.join(self.fields)+"}&limit=10000"

        data = requests.get(url + self.token)
        json_data = json.loads(data._content.decode("utf-8"))
        if process:
            df_data = pd.DataFrame(json_data["data"])
            df_data["product"] = df_data["name"].apply(lambda x: x.split("[")[1][:-2])
            df_data["kind"] = df_data["name"].apply(lambda x: x.split("]")[1][2:])
            df_data["second_kind"] = df_data["name"].apply(lambda x: x.split("[")[3].split("]")[0] if x.count('[') > 2 else "")
            return df_data.sort_values(by="name")
        else:
            return json_data

    def get_adset_status(self, since_until=None, date_preset=None, increment='all_days', process=True):
        url = self.base_url + "act_" + str(self.ad_acc)
        url += "/adsets?fields=name,status,id, daily_budget, campaign_id, ads{name, id, status}, campaign{name},insights"

        if since_until:
            url += '.time_range({since:"'+ since_until[0] +'", until:"'+ since_until[1] +'"})'
        elif date_preset:
            url+='.date_preset({})'.format(date_preset)
        if increment:
            url+='.time_increment({})'.format(increment)
        
        url += "{"+','.join(self.fields)+"}&limit=10000"
        data = requests.get(url + self.token)
        json_data = json.loads(data._content.decode("utf-8"))
        if process:
            df_data = pd.DataFrame(json_data["data"])
            df_data["campaign_name"] = df_data["campaign"].apply(lambda x: x["name"])
            df_data["product"] = df_data["campaign_name"].apply(lambda x: x.split("[")[1][:-2])
            df_data["kind"] = df_data["campaign_name"].apply(lambda x: x.split("]")[1][2:])
            df_data["second_kind"] = df_data["campaign_name"].apply(lambda x: x.split("[")[3].split("]")[0] if x.count('[') > 2 else "")
            return df_data.sort_values(by="name")
        else:
            return json_data

    def get_ads_status(self, since_until=None, date_preset=None, increment='all_days', process=True, effective_status=['PAUSED','ACTIVE','CAMPAIGN_PAUSED','ADSET_PAUSED'], impressions=0, filter='GREATER_THAN'):
        url = self.base_url + "act_" + str(self.ad_acc)
        url += "/ads?fields=name,status,campaign{name,objective},adset{name},preview_shareable_link,targetingsentencelines,adcreatives{instagram_permalink_url,thumbnail_url},insights"
        #url += "/ads?fields=name,status,campaign{name,objective},adset{name},insights"

        if since_until:
            url += '.time_range({since:"'+ since_until[0] +'", until:"'+ since_until[1] +'"})'
        elif date_preset:
            url+='.date_preset({})'.format(date_preset)
        if increment:
            url+='.time_increment({})'.format(increment)
        
        url += "{"+','.join(self.fields)+"}&limit=10000&filtering=[{'field': 'effective_status', 'operator':'IN', 'value':"+str(effective_status)+"},{field: 'impressions', operator:'"+str(filter)+"', 'value':"+str(impressions)+"}]"
        #&filtering=[{'field': 'effective_status', 'operator':'IN', 'value':['PAUSED','ACTIVE','CAMPAIGN_PAUSED','ADSET_PAUSED']}]"
        #&filtering=[{field: 'impressions', operator:'GREATER_THAN', value:'0'}]
        data = requests.get(url + self.token)
        json_data = json.loads(data._content.decode("utf-8"))
        if process:
            df_data = pd.DataFrame(json_data["data"])
            df_data["campaign_name"] = df_data["campaign"].apply(lambda x: x["name"])
            df_data["objective"] = df_data["campaign"].apply(lambda x: x["objective"])
            df_data["product"] = df_data["campaign_name"].apply(lambda x: x.split("[")[1][:-2])
            df_data["kind"] = df_data["campaign_name"].apply(lambda x: x.split("]")[1][2:])
            df_data["second_kind"] = df_data["campaign_name"].apply(lambda x: x.split("[")[3].split("]")[0] if x.count('[') > 2 else "")
            df_data["adset_name"] = df_data["adset"].apply(lambda x: x["name"])
            df_data["insta_link"] = df_data["adcreatives"].apply(lambda x: x["data"][0].get("instagram_permalink_url"))
            df_data["thumb_link"] = df_data["adcreatives"].apply(lambda x: x["data"][0].get("thumbnail_url"))
            return df_data.sort_values(by="name")
        else:
            return json_data

    def get_data_over_time(self, campaign):
        url = self.base_url + str(campaign)
        url += "/insights?fields="+ ",".join(self.api_fields)
        url += "&date_preset=last_30d&time_increment=1"

        data = requests.get(url + self.token)
        data = json.loads(data._content.decode("utf-8"))
        for i in data["data"]:
            if "conversions" in i:
                i["conversion"] = float(i["conversions"][0]["value"])
        return data


    # ========================================
    # Function analysis
    def campaign_over_time(self, df, products, stats, kind=None):
        df = df[df["product"] == product.upper()] if product else df
        if kind:
            if '/' in kind:
                kind1, kind2 = kind.split("/")
                df = df[(df["kind"] ==kind1) & (df["second_kind"] ==kind2)]
            else:
                df = df[df['kind'].isin([kind] if type(kind) == str else kind)] if kind else df
        return self.process_insights(df, stats)

    def process_insights(self, df, stats, products=None, kinds=None):
        df_stats = pd.DataFrame()
        df = df[df["kind"].apply(lambda x: x in kinds)] if kinds else df
        df = df[df["product"].apply(lambda x: x in products)] if products else df

        for idx, row in df.iterrows():
            data = copy.deepcopy(row["insights"]["data"])

            for data_line in data:
                for item in ['video_p25_watched_actions', 'video_p50_watched_actions', 'video_p75_watched_actions', 'purchase_roas']:            
                    data_line[item] = float(data_line[item][0]["value"]) if item in data_line.keys() else 0
                
                for item in data_line["actions"]:
                    data_line[item["action_type"]] = item["value"]
                    # if stats == 'purchase_roas':
                        # print(stats, data_line[stats])
                    data_line[stats] = 0 if stats not in data_line.keys() else float(data_line[stats])
                del data_line["actions"]
            
            df_data = pd.DataFrame(data)
            df_data["date_start"] = pd.to_datetime(df_data["date_start"])
            df_stats = df_stats.join(df_data.set_index("date_start")[[stats]].rename(columns={stats:row["name"]}), how='outer')
        return df_stats

    def campaigns_report(self, df_camp, products, stats, kinds=None, pivot=True):
        data = []
        kinds = df_camp["kind"].unique() if not kinds else kinds

        for product in products:
            for kind in kinds:
                dict_stats = {}
                df_slice = df_camp[df_camp["product"] == product.upper()].copy()
                df_slice = df_slice[df_slice["kind"] == kind.upper()].copy()
                df_spend = self.process_insights(df_slice, "spend")
                campaigns = df_slice["name"].unique() 

                for col in campaigns:
                    dict_stats['kind'] = kind
                    dict_stats['campaign'] = col

                    for stat in stats:
                        df_aux = self.process_insights(df_slice, stat)
                        
                        if stat not in self.mean_based_fields:
                            dict_stats[stat] = df_aux[[col]].apply(np.sum).values[0]
                        else:
                            dict_stats[stat] = ((df_aux[[col]] * df_spend[[col]]).sum() / df_spend[[col]].sum()).values[0]
                    
                    data+= [{"product": product.upper()} | dict_stats]

        df_data = pd.DataFrame(data)
        dict_map = df_camp.set_index("name")["objective"].to_dict()
        df_data["objective"] = df_data["campaign"].map(dict_map)
        return df_data.pivot_table(index=["product", "kind", "campaign", "objective"]) if pivot else df_data

    def adsets_report(self, df_adsets, df_camp, products, stats=[], campaigns=None, adsets_with=''):
        data = []
        for product in products:
            df_conv = df_camp[(df_camp["kind"] == campaigns)].copy() if campaigns else df_camp.copy()
            df_conv = df_conv[(df_conv["product"] == product.upper())].copy()
            
            for idx, row in df_conv.iterrows():
                df_aux = df_adsets[df_adsets["campaign_id"] == row["id"]]
                
                for idx2, row2 in df_aux.iterrows():
                    if adsets_with.upper() not in row2['name'].upper():
                        continue
                    
                    dict_stats = {}
                    for stat in stats:
                        op = np.mean if stat in self.mean_based_fields else np.sum
                        dict_stats[stat] = self.process_insights(row2.to_frame().transpose(), stat).apply(op).values[0]
                    data+= [{"product": product.upper(), "name":  row['name'], 'adset': row2["name"]} | dict_stats]

        return pd.DataFrame(data)#pivot_table(index=["product", "name", "adset"])
        

    # ========================================
    # Function analysis




# act_3120164588217844/campaigns?fields=name,status, adsets
if __name__ == "__main__":
    fb_api = open("tokens/fb_token").read()
    ad_acc = "3120164588217844"

    self = GraphAPI(ad_acc, fb_api)

    from datetime import datetime
    df_campaigns = self.get_campaigns_status(since_until=['2022-09-17', datetime.today().strftime("%Y-%m-%d")], increment=1)
    df_campaigns["daily_budget"] = df_campaigns["daily_budget"].fillna(value=0).astype(int) / 100

    # Filtrando para campanhas ativas e que tiveram alguma veiculação no período
    df_camp = df_campaigns[df_campaigns["status"] == "ACTIVE"]
    df_camp_full = df_campaigns[df_campaigns['insights'].notna()]
    

    products = ['ML']
    kinds = ["ESCALA"]
    df = self.campaigns_report(df_camp_full, products, stats=['spend', 'purchase_roas'])


    self.get_insights(ad_acc)
    self.get_campaigns_status(ad_acc)["data"]