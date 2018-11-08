#!/usr/bin/env python

import argparse
import glob
import os.path
import logging
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mops_emission as mem
from sklearn import linear_model

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

mem.init_emission("fuel_and_emission_table.csv")

DEFAULT_AIRPORT = "KCLT"
DEFAULT_FFS_VERSION = "1.0"

KGS_TO_LBS = 2.20462
GMS_TO_LBS = KGS_TO_LBS/1000
LBS_TO_METRIC_TONS = 1/(KGS_TO_LBS*1000)
METRIC_TONS_CO2_TO_URBAN_TREES = 1/0.039

def main(ffs_path, ffs_version, airport):
    flight_list_included = []

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    logger.info("Begin loading data at {}".format(dt.datetime.now()))
    df0 = load_ffs_data(ffs_path, airport, ffs_version)
    logger.info("Finish loading data at {}".format(dt.datetime.now()))

    logger.info("Begin modifying data at {}".format(dt.datetime.now()))
    df1 = modify_data(df0)
    logger.info("Finish modifying data at {}".format(dt.datetime.now()))

    outputSuffix = dt.datetime.now().strftime("%Y%m%d")

    logger.info("Begin computing APREQ-all metrics at {}".format(
            dt.datetime.now()))


    #### compute GS first

    logger.info("Begin computing GS-all metrics at {}".format(
            dt.datetime.now()))
    ######### GS metrics
    [gs_all,flight_list_included] = gs_metrics_by_group(df1, None,flight_list_included)
    ######### GS metrics
    gs_all.to_csv("gs_benefits_airport_wide_{}.csv".format(
            outputSuffix), index=False)
    logger.info("Finish computing GS-all metrics at {}".format(
            dt.datetime.now()))


    #### compute general EDCT


    logger.info("Begin computing EDCT-all metrics at {}".format(
            dt.datetime.now()))
    ######### EDCT metrics
    [edct_all,flight_list_included] = edct_metrics_by_group(df1, None, flight_list_included)
    ######### EDCT metrics
    edct_all.to_csv("edct_benefits_airport_wide_{}.csv".format(
            outputSuffix), index=False)
    logger.info("Finish computing EDCT-all metrics at {}".format(
            dt.datetime.now()))



    logger.info("Begin computing APREQ-all metrics at {}".format(
             dt.datetime.now()))
    ######### APREQ metrics
    [apreq_all,flight_list_included] = apreq_metrics_by_group(df1, None,flight_list_included)
    ######### APREQ metrics
    apreq_all.to_csv("apreq_benefits_airport_wide_{}.csv".format(
            outputSuffix), index=False)
    plot_apreq_benefits(apreq_all, outputSuffix)
    logger.info("Finish computing APREQ-all metrics at {}".format(
            dt.datetime.now()))

    # logger.info("Begin computing APREQ-AAL metrics at {}".format(
    #         dt.datetime.now()))
    # apreq_aal = apreq_metrics_by_group(df1, "aal_mainline")
    # apreq_aal.to_csv("apreq_benefits_AAL_mainline_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing APREQ-AAL metrics at {}".format(
    #         dt.datetime.now()))

    # logger.info("Begin computing APREQ-regional metrics at {}".format(
    #         dt.datetime.now()))
    # apreq_reg = apreq_metrics_by_group(df1, "aal_regional")
    # apreq_reg.to_csv("apreq_benefits_AAL_regional_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing APREQ-regional metrics at {}".format(
    #         dt.datetime.now()))

    logger.info("Begin computing metering-all metrics at {}".format(
            dt.datetime.now()))
    ######### Meter metrics
    [meter_all,flight_list_included] = metering_metrics_by_group(df1, None, airport,flight_list_included)
    ######### Meter metrics
    meter_all.to_csv("hold_benefits_airport_wide_{}.csv".format(
            outputSuffix), index=False)
    plot_surface_metering_benefits(meter_all, outputSuffix)
    logger.info("Finish computing metering-all metrics at {}".format(
            dt.datetime.now()))

    # logger.info("Begin computing metering-AAL metrics at {}".format(
    #         dt.datetime.now()))
    # meter_aal = metering_metrics_by_group(df1, "aal_mainline", airport)
    # meter_aal.to_csv("hold_benefits_AAL_mainline_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing metering-AAL metrics at {}".format(
    #         dt.datetime.now()))

    # logger.info("Begin computing metering-regional metrics at {}".format(
    #         dt.datetime.now()))
    # meter_reg = metering_metrics_by_group(df1, "aal_regional", airport)
    # meter_reg.to_csv("hold_benefits_AAL_regional_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing metering-regional metrics at {}".format(
    #         dt.datetime.now()))

    

    # logger.info("Begin computing EDCT-AAL metrics at {}".format(
    #         dt.datetime.now()))
    # edct_aal = edct_metrics_by_group(df1, "aal_mainline")
    # edct_aal.to_csv("edct_benefits_AAL_mainline_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing EDCT-AAL metrics at {}".format(
    #         dt.datetime.now()))

    # logger.info("Begin computing EDCT-regional metrics at {}".format(
    #         dt.datetime.now()))
    # edct_reg = edct_metrics_by_group(df1, "aal_regional")
    # edct_reg.to_csv("edct_benefits_AAL_regional_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing EDCT-regional metrics at {}".format(
    #         dt.datetime.now()))

    

    # logger.info("Begin computing GS-AAL metrics at {}".format(
    #         dt.datetime.now()))
    # gs_aal = gs_metrics_by_group(df1, "aal_mainline")
    # gs_aal.to_csv("gs_benefits_AAL_mainline_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing GS-AAL metrics at {}".format(
    #         dt.datetime.now()))

    # logger.info("Begin computing GS-regional metrics at {}".format(
    #         dt.datetime.now()))
    # gs_reg = gs_metrics_by_group(df1, "aal_regional")
    # gs_reg.to_csv("gs_benefits_AAL_regional_{}.csv".format(
    #         outputSuffix), index=False)
    # logger.info("Finish computing GS-regional metrics at {}".format(
    #         dt.datetime.now()))

    logger.info("Begin computing summary of benefits at {}".format(
            dt.datetime.now()))
    summary = summarize_benefits(apreq_all, meter_all, edct_all, gs_all)
    summary.to_csv("summary_benefits_metrics_{}.csv".format(
            outputSuffix), index=False)
    logger.info("Finish computing summary of benefits at {}".format(
            dt.datetime.now()))

#TODO: clean up this function
def summarize_benefits(df_apreq, df_hold, df_edct, df_gs):
    df_summary = pd.DataFrame()
    
    idac_time_saved_hour = df_apreq['Time saved by IDAC-related APREQ negotiation (hours)'].sum()
    apreq_time_gate_hold_hour = df_apreq['Gate hold flights with APREQ negotiated at gate (Hours)'].sum()
    meter_time_gate_hold_hour = df_hold['Sum of surface metering gate holds (minutes)'].sum() / float(60)
    edct_gate_hold_hour = df_edct["Sum of EDCT gate holds (hours)"].sum()
    gs_gate_hold_hour = df_gs["Sum of GS gate holds (hours)"].sum()
    #### Pounds Fuel
    surface_metering_pounds_fuel = df_hold['Fuel saved by surface metering gate holds (pounds)'].sum()
    apreq_gate_hold_pounds_fuel = df_apreq['Fuel saved by gate holds of flights with APREQ negotiated at gate (pounds)'].sum()
    IDAC_renegotiation_pounds_fuel = df_apreq['Fuel saved by IDAC-related APREQ negotiation (pounds)'].sum()
    edct_gate_hold_pounds_fuel = df_edct["Fuel saved by EDCT gate holds (pounds)"].sum()
    gs_gate_hold_pounds_fuel = df_gs["Fuel saved by GS gate holds (pounds)"].sum()
    #### Pounds CO2
    surface_metering_pounds_CO2 = df_hold['CO2 saved by surface metering gate holds (pounds)'].sum()
    apreq_gate_hold_pounds_CO2 = df_apreq['CO2 saved by gate holds of flights with APREQ negotiated at gate (pounds)'].sum()
    IDAC_renegotiation_pounds_CO2 = df_apreq['CO2 saved by IDAC-related APREQ negotiation (pounds)'].sum()
    edct_gate_hold_pounds_CO2 = df_edct["CO2 saved by EDCT gate holds (pounds)"].sum()
    gs_gate_hold_pounds_CO2 = df_gs["CO2 saved by GS gate holds (pounds)"].sum()
    #### Urban Trees
    surface_metering_urban_trees = df_hold['Urban trees saved'].sum()
    apreq_gate_hold_urban_trees = df_apreq['Urban trees saved by gate holds of flights with APREQ negotiated at gate'].sum()
    IDAC_renegotiation_urban_trees = df_apreq['Urban trees saved by IDAC APREQ negotiation'].sum()
    edct_gate_hold_urban_trees = df_edct["Urban trees saved"].sum()
    gs_gate_hold_urban_trees = df_gs["Urban trees saved"].sum()
    
    df_summary.loc[0,'IDAC_delay_savings(hours)'] = idac_time_saved_hour
    df_summary.loc[0,'surface_metering_engine_run_time_savings(hours)'] = meter_time_gate_hold_hour
    df_summary.loc[0,'APREQ_gate_hold_engine_run_time_savings(hours)'] = apreq_time_gate_hold_hour
    df_summary.loc[0,"EDCT_gate_hold_engine_run_time_savings(hours)"] = edct_gate_hold_hour
    df_summary.loc[0,"GS_gate_hold_engine_run_time_savings(hours)"] = gs_gate_hold_hour
    df_summary.loc[0,'total_engine_run_time_savings(hours)'] = (
            df_summary.loc[0,'IDAC_delay_savings(hours)'] +
            df_summary.loc[0,'surface_metering_engine_run_time_savings(hours)'] +
            df_summary.loc[0,'APREQ_gate_hold_engine_run_time_savings(hours)'] +
            df_summary.loc[0,"EDCT_gate_hold_engine_run_time_savings(hours)"] +
            df_summary.loc[0,"GS_gate_hold_engine_run_time_savings(hours)"])
            
    #### Surface Metering
    df_summary.loc[0,'surface_metering_fuel(pounds)'] = surface_metering_pounds_fuel
    df_summary.loc[0,'surface_metering_CO2(pounds)'] = surface_metering_pounds_CO2
    df_summary.loc[0,'surface_metering_urban_trees'] = surface_metering_urban_trees
    #### APREQ Gate Hold
    df_summary.loc[0,'APREQ_gate_hold_fuel(pounds)'] = apreq_gate_hold_pounds_fuel
    df_summary.loc[0,'APREQ_gate_hold_CO2(pounds)'] = apreq_gate_hold_pounds_CO2
    df_summary.loc[0,'APREQ_gate_hold_urban_trees'] = apreq_gate_hold_urban_trees
    #### IDAC Renegotiation
    df_summary.loc[0,'IDAC_renegotiation_fuel(pounds)'] = IDAC_renegotiation_pounds_fuel
    df_summary.loc[0,'IDAC_renegotiation_CO2(pounds)'] = IDAC_renegotiation_pounds_CO2
    df_summary.loc[0,'IDAC_renegotiation_urban_trees'] = IDAC_renegotiation_urban_trees
    
    df_summary.loc[0,"EDCT_gate_hold_fuel(pounds)"] = edct_gate_hold_pounds_fuel
    df_summary.loc[0,"EDCT_gate_hold_CO2(pounds)"] = edct_gate_hold_pounds_CO2
    df_summary.loc[0,"EDCT_gate_hold_urban_trees"] = edct_gate_hold_urban_trees

    df_summary.loc[0,"GS_gate_hold_fuel(pounds)"] = gs_gate_hold_pounds_fuel
    df_summary.loc[0,"GS_gate_hold_CO2(pounds)"] = gs_gate_hold_pounds_CO2
    df_summary.loc[0,"GS_gate_hold_urban_trees"] = gs_gate_hold_urban_trees
    
    df_summary.loc[0,'total_fuel(pounds)'] = (
            df_summary.loc[0,'surface_metering_fuel(pounds)'] +
            df_summary.loc[0,'APREQ_gate_hold_fuel(pounds)'] +
            df_summary.loc[0,'IDAC_renegotiation_fuel(pounds)'] +
            df_summary.loc[0,"EDCT_gate_hold_fuel(pounds)"] +
            df_summary.loc[0,"GS_gate_hold_fuel(pounds)"])
    
    df_summary.loc[0,'total_CO2(pounds)'] = (
            df_summary.loc[0,'surface_metering_CO2(pounds)'] +
            df_summary.loc[0,'APREQ_gate_hold_CO2(pounds)'] +
            df_summary.loc[0,'IDAC_renegotiation_CO2(pounds)'] +
            df_summary.loc[0,"EDCT_gate_hold_CO2(pounds)"] +
            df_summary.loc[0,"GS_gate_hold_CO2(pounds)"])
    
    df_summary.loc[0,'total_urban_trees'] = (
            df_summary.loc[0,'surface_metering_urban_trees'] +
            df_summary.loc[0,'APREQ_gate_hold_urban_trees'] +
            df_summary.loc[0,'IDAC_renegotiation_urban_trees'] +
            df_summary.loc[0,"EDCT_gate_hold_urban_trees"] +
            df_summary.loc[0,"GS_gate_hold_urban_trees"])
    
    df_summary.loc[0,'IDAC_passenger_value_of_time'] =  df_summary.loc[0,'IDAC_delay_savings(hours)'] * float(4800.20)
    df_summary.loc[0,'IDAC_flight_crew_cost'] = df_summary.loc[0,'IDAC_delay_savings(hours)'] * 60 * float(22.67)
    
    df_summary.loc[0,'surface_metering_fuel(gallons jet A-1 6.71 pounds / gal)'] = surface_metering_pounds_fuel / float(6.71)
    df_summary.loc[0,'surface_metering_fuel(gallons jet A 6.84 pounds / gal)'] = surface_metering_pounds_fuel / float(6.84)
    
    df_summary.loc[0,'APREQ_gate_hold_fuel(gallons jet A-1 6.71 pounds / gal)'] = apreq_gate_hold_pounds_fuel / float(6.71)
    df_summary.loc[0,'APREQ_gate_hold_fuel(gallons jet A 6.84 pounds / gal)'] = apreq_gate_hold_pounds_fuel / float(6.84)
    
    df_summary.loc[0,'IDAC_renegotiation_fuel(gallons jet A-1 6.71 pounds / gal)'] = IDAC_renegotiation_pounds_fuel / float(6.71)
    df_summary.loc[0,'IDAC_renegotiation_fuel(gallons jet A 6.84 pounds / gal)'] = IDAC_renegotiation_pounds_fuel / float(6.84)

    df_summary.loc[0,'EDCT_gate_hold_fuel(gallons jet A-1 6.71 pounds / gal)'] = edct_gate_hold_pounds_fuel / float(6.71)
    df_summary.loc[0,'EDCT_gate_hold_fuel(gallons jet A 6.84 pounds / gal)'] = edct_gate_hold_pounds_fuel / float(6.84)

    df_summary.loc[0,'GS_gate_hold_fuel(gallons jet A-1 6.71 pounds / gal)'] = gs_gate_hold_pounds_fuel / float(6.71)
    df_summary.loc[0,'GS_gate_hold_fuel(gallons jet A 6.84 pounds / gal)'] = gs_gate_hold_pounds_fuel / float(6.84)
    
    df_summary.loc[0,'total_fuel(gallons jet A-1 6.71 pounds / gal)'] = df_summary.loc[0,'total_fuel(pounds)'] / float(6.71)
    df_summary.loc[0,'total_fuel(gallons jet A 6.84 pounds / gal)'] = df_summary.loc[0,'total_fuel(pounds)'] / float(6.84)

    return df_summary

def edct_metrics_by_group(df, group, flight_list):
    if group:
        idx_group = df["flight_category"] == group
    else:
        idx_group = df["gufi"].notnull()

    idx_date = df["year_month"] != "nan-nan"
    idx_edct = df["edct_at_ready"].notnull()

    df_edct = df[idx_group & idx_date & idx_edct] 
    print('EDCT pre filter')
    print(len(df_edct))
    ##### Filter out flights found previously
    df_edct = df_edct[~df_edct['gufi'].isin(flight_list)]
    print('EDCT post filter')
    print(len(df_edct))
    df_temp = df_edct[df_edct['effective_gate_hold']>0]
    print('EDCT actually held')
    print(len(df_temp))
    ##### Add flights to flight list
    flight_list.extend( df_edct['gufi'].values.tolist() )


    df_edct[["hold_savings_fuel",
             "hold_savings_co",
             "hold_savings_co2",
             "hold_savings_hc",
             "hold_savings_nox"]] = df_edct.apply(
                     calc_emissions, axis=1, args=["effective_gate_hold"])

    edct_metrics = (
            df_edct.groupby(["year_month"]).agg(
            {"gufi":"count",
             "effective_gate_hold":lambda x: sum(x)/3600,
             "hold_savings_fuel":lambda x: np.nansum(x)*KGS_TO_LBS,
             "hold_savings_co":lambda x: np.nansum(x)*GMS_TO_LBS,
             "hold_savings_co2":lambda x: np.nansum(x)*KGS_TO_LBS,
             "hold_savings_hc":lambda x: np.nansum(x)*GMS_TO_LBS,
             "hold_savings_nox":lambda x: np.nansum(x)*GMS_TO_LBS}).
            reset_index())

    edct_metrics = edct_metrics.assign(
            urban_trees_planted=edct_metrics["hold_savings_co2"]*
            LBS_TO_METRIC_TONS*METRIC_TONS_CO2_TO_URBAN_TREES)

    edct_metrics = edct_metrics.rename(columns={
            "gufi":"Count of EDCT flights",
            "effective_gate_hold":"Sum of EDCT gate holds (hours)",
            "hold_savings_fuel":"Fuel saved by EDCT gate holds (pounds)",
            "hold_savings_co":"CO saved by EDCT gate holds (pounds)",
            "hold_savings_co2":"CO2 saved by EDCT gate holds (pounds)",
            "hold_savings_hc":"HC saved by EDCT gate holds (pounds)",
            "hold_savings_nox":"NOX saved by EDCT gate holds (pounds)",
            "urban_trees_planted":"Urban trees saved"})

    return [edct_metrics,flight_list]

def gs_metrics_by_group(df, group, flight_list):
    if group:
        idx_group = df["flight_category"] == group
    else:
        idx_group = df["gufi"].notnull()

    idx_date = df["year_month"] != "nan-nan"
    idx_gs = df["ground_stop_restriction_ids_present"] == True

    df_gs = df[idx_group & idx_date & idx_gs]
    print('GS pre filter')
    print(len(df_gs))
    ##### Filter out flights found previously
    df_gs = df_gs[~df_gs['gufi'].isin(flight_list)]
    print('GS post filter')
    print(len(df_gs))
    df_temp = df_gs[df_gs['effective_gate_hold']>0]
    print('Ground stop actually held')
    print(len(df_temp))
    ##### Add flights to flight list
    flight_list.extend( df_gs['gufi'].values.tolist() )
    
    logger.debug("Filtered GS data of shape {}".format(df_gs.shape))

    logger.debug("Begin computing emissions at {}".format(dt.datetime.now()))
    df_gs[["hold_savings_fuel",
             "hold_savings_co",
             "hold_savings_co2",
             "hold_savings_hc",
             "hold_savings_nox"]] = df_gs.apply(
                     calc_emissions, axis=1, args=["effective_gate_hold"])
    logger.debug("Finish computing emissions at {}".format(dt.datetime.now()))

    gs_metrics = (
            df_gs.groupby(["year_month"]).agg(
            {"gufi":"count",
             "effective_gate_hold":lambda x: sum(x)/3600,
             "hold_savings_fuel":lambda x: np.nansum(x)*KGS_TO_LBS,
             "hold_savings_co":lambda x: np.nansum(x)*GMS_TO_LBS,
             "hold_savings_co2":lambda x: np.nansum(x)*KGS_TO_LBS,
             "hold_savings_hc":lambda x: np.nansum(x)*GMS_TO_LBS,
             "hold_savings_nox":lambda x: np.nansum(x)*GMS_TO_LBS}).
            reset_index())

    gs_metrics = gs_metrics.assign(
            urban_trees_planted=gs_metrics["hold_savings_co2"]*
            LBS_TO_METRIC_TONS*METRIC_TONS_CO2_TO_URBAN_TREES)

    gs_metrics = gs_metrics.rename(columns={
            "gufi":"Count of GS flights",
            "effective_gate_hold":"Sum of GS gate holds (hours)",
            "hold_savings_fuel":"Fuel saved by GS gate holds (pounds)",
            "hold_savings_co":"CO saved by GS gate holds (pounds)",
            "hold_savings_co2":"CO2 saved by GS gate holds (pounds)",
            "hold_savings_hc":"HC saved by GS gate holds (pounds)",
            "hold_savings_nox":"NOX saved by GS gate holds (pounds)",
            "urban_trees_planted":"Urban trees saved"})

    return [gs_metrics,flight_list]


def plot_surface_metering_benefits(df_hold, decorator):
    df_hold = (df_hold[((df_hold["year_month"].notnull()) &
                       (df_hold["year_month"] != "2017-10"))].
               sort_values("year_month").
               reset_index())
    co2 = np.array(
            df_hold["CO2 saved by surface metering gate holds (pounds)"])
    plt.figure(figsize=(30,8))
    x_vec = np.arange(len(co2))
    plt.bar(x_vec, co2/float(1000),
            color="green", alpha=0.5, edgecolor="black")
    plt.ylabel("CO2 Emissions Savings\n(thousand pounds)", fontsize=30)
    plt.xticks(x_vec, df_hold["year_month"], fontsize=20)
    plt.yticks(fontsize=30)
    plt.title("Total Estimated CO2 Emissions Savings",
              fontsize=40)
    ax = plt.gca()
    ax.yaxis.grid(True)
    plt.savefig("hold_estimated_savings_{}.png".format(decorator))

def plot_apreq_benefits(df_apreq, decorator):
    df_apreq = df_apreq.sort_values("year_month").reset_index()
    df_apreq = df_apreq.assign(
            fuel_per_apreq=df_apreq["Fuel saved by gate holds of flights with APREQ negotiated at gate (pounds)"]
                / df_apreq["Count of flights with first APREQ negotiated at gate"])
    fuel_per_apreq = np.array(df_apreq["fuel_per_apreq"])
    plt.figure(figsize=(12,10))
    x_vec = np.arange(len(fuel_per_apreq))
    plt.plot(x_vec, fuel_per_apreq, linewidth=10, color="blue", alpha=0.6)
    plt.plot(x_vec, fuel_per_apreq,
             linestyle="None", marker="o", markersize=30,
             color="blue", alpha=0.9)
    plt.xticks(x_vec, df_apreq["year_month"], fontsize=20, rotation=30)
    plt.ylabel("Fuel Saved per APREQ (pounds)", fontsize=24)
    plt.title("Fuel Saved per APREQ Flight\nScheduled at Gate", fontsize=50)
    plt.yticks(fontsize=16)
    plt.tight_layout()
    ax = plt.gca()
    ax.yaxis.grid(True)

    regr = linear_model.LinearRegression()
    regr.fit(x_vec.reshape(-1, 1), fuel_per_apreq.reshape(-1, 1))
    slope = regr.coef_[0][0]
    y_intercept = regr.intercept_[0]

    y2 = (len(x_vec)-1) * slope + y_intercept
    plt.plot([0,len(x_vec)-1], [y_intercept, y2 ],
              linestyle="-.", linewidth=6, color="red")
    plt.savefig("apreq_estimated_savings_{}.png".format(decorator))

def metering_metrics_by_group(df, group, airport,flight_list):
    if group:
        idx_group = df["flight_category"] == group
    else:
        idx_group = df["gufi"].notnull()

    idx_date = df["year_month"] != "nan-nan"
    idx_meter = df["metered_indicator"] == True

    metrics = df[idx_group & idx_date & idx_meter]
    print('metering pre filter')
    print(len(metrics))
    ##### Filter out flights found previously
    debug_df = metrics[metrics['gufi'].isin(flight_list)]
    debug_df.to_csv('surface_metered_flights_filtered_out.csv',index=False)
    metrics = metrics[~metrics['gufi'].isin(flight_list)]
    metrics.to_csv('debug_surface_metered_flights.csv')
    print('metering post filter')
    print(len(metrics))
    temp_metrics = metrics[metrics['hold_indicator']==True]
    print('number actually held')
    print(len(temp_metrics))
    ##### Add flights to flight list
    flight_list.extend( metrics['gufi'].values.tolist() )

    metrics = metrics.groupby(["year_month"]).agg(
                     {"departure_aerodrome_icao_name":lambda x: sum(x == airport),
                      "hold_indicator":"sum",
                      "actual_gate_hold":"sum",
                      "gate_hold_fuel_savings":lambda x: np.nansum(x)*KGS_TO_LBS,
                      "gate_hold_co_savings":lambda x: np.nansum(x)*GMS_TO_LBS,
                      "gate_hold_co2_savings":lambda x: np.nansum(x)*KGS_TO_LBS,
                      "gate_hold_hc_savings":lambda x: np.nansum(x)*GMS_TO_LBS,
                      "gate_hold_nox_savings":lambda x: np.nansum(x)*GMS_TO_LBS}).\
              reset_index()
    metrics = metrics.assign(urban_trees_planted = metrics["gate_hold_co2_savings"]* \
                  LBS_TO_METRIC_TONS* \
                  METRIC_TONS_CO2_TO_URBAN_TREES)

    metrics.rename(
            columns={"departure_aerodrome_icao_name":"Count of departures",
                     "hold_indicator":"Count of departures held",
                     "actual_gate_hold":"Sum of surface metering gate holds (minutes)",
                     "gate_hold_fuel_savings":"Fuel saved by surface metering gate holds (pounds)",
                     "gate_hold_co_savings":"CO saved by surface metering gate holds (pounds)",
                     "gate_hold_co2_savings":"CO2 saved by surface metering gate holds (pounds)",
                     "gate_hold_hc_savings":"HC saved by surface metering gate holds (pounds)",
                     "gate_hold_nox_savings":"NOX saved by surface metering gate holds (pounds)",
                     "urban_trees_planted":"Urban trees saved"},
            inplace=True)

    return [metrics,flight_list]

def apreq_metrics_by_group(df, group,flight_list):
    idx_idac_savings = df["apreq_final"] < df["apreq_initial"]
    idx_all_idac = ((df["apreq_initial_source"] == "IDAC") &
                   (df["apreq_final_source"] == "IDAC"))
    if group:
        idx_group = df["flight_category"] == group
    else:
        idx_group = df["gufi"].notnull()

    idx_neg_at_gate = (
            df["surface_flight_state_at_initial_apreq"] == "SCHEDULED")
    idx_reasonable_holds = (df["effective_gate_hold"] <= 1800)

    idx_date = df["year_month"] != "nan-nan"

    df_idac = df[idx_group &
                 idx_idac_savings &
                 idx_all_idac &
                 idx_date]

    #### DONT FILTER FLIGHTS FROM RENEGOTIATION SAVINGS
    # print(len(df_idac))
    # ##### Filter out flights found previously
    # df_idac = df_idac[~df_idac['gufi'].isin(flight_list)]
    # print(len(df_idac))
    # ##### Add flights to flight list
    # flight_list.extend( df_idac['gufi'].values.tolist() )
    print('Number of IDAC renegotiation')
    print(len(df_idac))



    
    df_idac[["IDAC_savings_fuel",
             "IDAC_savings_co",
             "IDAC_savings_co2",
             "IDAC_savings_hc",
             "IDAC_savings_nox"]] = df_idac.apply(
                         calc_emissions, axis=1, args=["negotiation_savings"])

    idac_metrics = (
            df_idac.groupby(["year_month"]).agg(
            {"gufi":"count",
             "negotiation_savings":lambda x: sum(x)/3600,
             "IDAC_savings_fuel":lambda x: np.nansum(x)*KGS_TO_LBS,
             "IDAC_savings_co":lambda x: np.nansum(x)*GMS_TO_LBS,
             "IDAC_savings_co2":lambda x: np.nansum(x)*KGS_TO_LBS,
             "IDAC_savings_hc":lambda x: np.nansum(x)*GMS_TO_LBS,
             "IDAC_savings_nox":lambda x: np.nansum(x)*GMS_TO_LBS}).
            reset_index())

    idac_metrics = idac_metrics.assign(
            IDAC_trees_planted = \
                idac_metrics["IDAC_savings_co2"]* \
                LBS_TO_METRIC_TONS* \
                METRIC_TONS_CO2_TO_URBAN_TREES)

    idac_metrics.rename(columns={
            "gufi":
                "Count of flights with IDAC-related time savings",
            "negotiation_savings":
                "Time saved by IDAC-related APREQ negotiation (hours)",
            "IDAC_savings_fuel":
                "Fuel saved by IDAC-related APREQ negotiation (pounds)",
            "IDAC_savings_co":
                "CO saved by IDAC-related APREQ negotiation (pounds)",
            "IDAC_savings_co2":
                "CO2 saved by IDAC-related APREQ negotiation (pounds)",
            "IDAC_savings_hc":
                "HC saved by IDAC-related APREQ negotiation (pounds)",
            "IDAC_savings_nox":
                "NOX saved by IDAC-related APREQ negotiation (pounds)",
            "IDAC_trees_planted":
                "Urban trees saved by IDAC APREQ negotiation"},
            inplace=True)

    hold_metrics_df = df[idx_group &
                         idx_neg_at_gate &
                         idx_reasonable_holds &
                         idx_date]

    ##### FILTER EDCT / GS that might also have APREQ and gate hold
    print('APREQ gate hold pre filter')
    print(len(hold_metrics_df))
    ##### Filter out flights found previously
    hold_metrics_df = hold_metrics_df[~hold_metrics_df['gufi'].isin(flight_list)]
    print(len(hold_metrics_df))
    print('APREQ gate hold post filter')

    df_temp = hold_metrics_df[ hold_metrics_df['effective_gate_hold']>0]

    print('Number of APREQ held')
    print(len(df_temp))
    ##### Add flights to flight list
    flight_list.extend( hold_metrics_df['gufi'].values.tolist() )

    hold_metrics_df[["hold_savings_fuel",
                     "hold_savings_co",
                     "hold_savings_co2",
                     "hold_savings_hc",
                     "hold_savings_nox"]] = hold_metrics_df.apply(
                         calc_emissions, axis=1, args=["effective_gate_hold"])

    hold_metrics = hold_metrics_df.groupby(["year_month"]).agg(
            {"gufi":"count",
             "effective_gate_hold":lambda x: np.nansum(x)/3600,
             "hold_savings_fuel":lambda x: np.nansum(x)*KGS_TO_LBS,
             "hold_savings_co":lambda x: np.nansum(x)*GMS_TO_LBS,
             "hold_savings_co2":lambda x: np.nansum(x)*KGS_TO_LBS,
             "hold_savings_hc":lambda x: np.nansum(x)*GMS_TO_LBS,
             "hold_savings_nox":lambda x: np.nansum(x)*GMS_TO_LBS}).\
            reset_index()
    hold_metrics = hold_metrics.assign(
            urban_trees_planted = \
                hold_metrics["hold_savings_co2"]* \
                LBS_TO_METRIC_TONS* \
                METRIC_TONS_CO2_TO_URBAN_TREES)
    hold_metrics.rename(columns={
            "gufi":
                "Count of flights with first APREQ negotiated at gate",
            "effective_gate_hold":
                "Gate hold flights with APREQ negotiated at gate (Hours)",
            "hold_savings_fuel":
                "Fuel saved by gate holds of flights with APREQ negotiated at gate (pounds)",
            "hold_savings_co":
                "CO saved by gate holds of flights with APREQ negotiated at gate (pounds)",
            "hold_savings_co2":
                "CO2 saved by gate holds of flights with APREQ negotiated at gate (pounds)",
            "hold_savings_hc":
                "HC saved by gate holds of flights with APREQ negotiated at gate (pounds)",
            "hold_savings_nox":
                "NOX saved by gate holds of flights with APREQ negotiated at gate (pounds)",
            "urban_trees_planted":
                "Urban trees saved by gate holds of flights with APREQ negotiated at gate"},
            inplace=True)
    metrics = idac_metrics.merge(hold_metrics, how="outer", on="year_month")

    return [metrics,flight_list]

def modify_data(df):
    df = df.assign(aobt_local=
            df.departure_stand_actual_time.dt.tz_localize("UTC").\
                                           dt.tz_convert("US/Eastern"))
    df["year_month"] = df.apply(
            lambda x: "{}-{}".format(x.aobt_local.year, x.aobt_local.month),
            axis=1)
    df = df.assign(negotiation_savings=
            (df.apreq_initial - df.apreq_final).dt.seconds)
    df = df.assign(effective_gate_hold=
            (df.departure_stand_actual_time - df.pilot_ready_time).dt.seconds)

    return df

def load_ffs_data(ffs_path, airport, ffs_version):
    allFiles = glob.glob(os.path.join(ffs_path, "**",
                   airport + ".fullFlightSummary.v" + ffs_version + "*.csv"),
        recursive=True)

    indiv_files = []
    for f in allFiles:
        df = pd.read_csv(f, index_col=None, header=0,
                         parse_dates=["time_at_initial_apreq",
                                      "apreq_initial",
                                      "apreq_final",
                                      "departure_stand_actual_time",
                                      "pilot_ready_time"])
        indiv_files.append(df)
    df = pd.concat(indiv_files)

    return df

def calc_emissions(row, field):
    em_input = pd.DataFrame({
            "aircraftType":row["aircraft_type"],
            "weightClass":"D",
            "MoveTAct":0,
            "RampTAct":0,
            "TaxiTAct":row[field]},
        index=[0])
    em_results = mem.row_get_total_emission(em_input.iloc[0])

    return pd.Series(list(em_results.iloc[0:5]),
                     index=["fuel", "co", "co2", "hc", "nox"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate aggregate metrics")
    parser.add_argument("ffs_path",
                        help="Path with fullFlightSummary files")
    parser.add_argument("--ffs_version",
                        default=DEFAULT_FFS_VERSION,
                        help="fullFlightSummary version to open")
    parser.add_argument("--airport",
                        default=DEFAULT_AIRPORT,
                        help="Airport to analyze, ICAO format")
    args = parser.parse_args()

    main(args.ffs_path, args.ffs_version, args.airport)
