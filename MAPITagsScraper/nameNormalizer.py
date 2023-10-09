import re
import typing
from enum import IntEnum

import inflection


from .utils import dedupPreservingOrder

__all__ = ("canonicalizeOrigName", "convertName")

useWordNinja = False

if useWordNinja:
	import wordninja
	wnModel = wordninja.LanguageModel('mapiWordNinjaModel.txt.gz')

numUnderscoreSeparatedStr = re.compile(r"([h-zH-Z]+[a-zA-Z]+|[a-zA-Z]+[h-zH-Z]+)_(\d+)$")
allowedKSIdRx = re.compile(r"^\w+$")
multipleUnderscoresRx = re.compile(r"_+")


def attachNumber(s: str) -> str:
	return numUnderscoreSeparatedStr.subn("\\1\\2", s)[0]

def fixMultipleUnderscores(s: str) -> str:
	return multipleUnderscoresRx.subn("_", s)[0]


W_POSTFIX = "_W"
A_POSTFIX = "_A"


def clearPostfixes(n: str) -> str:
	if n.endswith(W_POSTFIX):
		n = n[: -len(W_POSTFIX)]
	elif n.endswith(A_POSTFIX):
		n = n[: -len(A_POSTFIX)]
	return n

class OrigIdType(IntEnum):
	unknown = 0
	PID_TAG = 1
	PTAG = 2
	PR_TAG = 3
	INT_SCH_TAG = 4

origIdTypeToPrefixMapping = {
	OrigIdType.PID_TAG: "PidTag",
	OrigIdType.PTAG: "ptag",
	OrigIdType.PR_TAG: "PR_",
	OrigIdType.INT_SCH_TAG: "InternalSchema",
}

PR_TAG = origIdTypeToPrefixMapping[OrigIdType.PR_TAG]


def canonicalizeOrigName(n: str) -> str:
	"""Removes unneeded prefixes and postfixes from `-orig-id`s"""
	if n.startswith(PR_TAG):
		n = clearPostfixes(n)
	return n


wordsSplitterFilters = {
	OrigIdType.PR_TAG: (
		('emsmdb', 'ems_mdb'),
		('addrtype', 'addr_type'),
		('oraddress', 'or_address'),
		('storeeid', 'store_eid'),
		('_svreid', '_svr_eid'),
		('seqid', 'seq_id'),
		('draftid', 'draft_id'),
		('srchid', 'srch_id'),
		('oflid', 'ofl_id'),
		('entryid', 'entry_id'),
		('linkid', 'link_id'),
		('replacetime', 'replace_time'),
		('trackstatus', 'track_status'),
		('clientid', 'client_id'),
		('parentid', 'parent_id'),
		('enabledon', 'enabled_on'),
		('onserver', 'on_server'),
		('schdinfo_', 'schd_info_'),
		('_freebusy_', '_free_busy_'),
		('_mtsout_', '_mts_out_'),
		('_mtsin_', '_mts_in_'),
		('xmlstream', 'xml_stream'),
		('containerid', 'container_id'),
		('templateid', 'template_id'),
		('proposedendtime', 'proposed_end_time'),
		('proposedstarttime', 'proposed_starttime'),
		('starttime', 'start_time'),
		('contactphoto', 'contact_photo'),
		('freebusy', 'free_busy'),
		('sendpost', 'send_post'),
		('readpost', 'read_post'),
		('reportnote', 'report_note'),
		('sendnote', 'send_note'),
		('readnote', 'read_note'),
		('endtxt', 'end_txt'),
		('begintxt', 'begin_txt'),
		('bodytag', 'body_tag'),
		('migrateprofile', 'migrate_profile'),
		('changenum', 'change_num'),
		('versionhistory', 'version_history'),
		('versionskeleton', 'version_skeleton'),
		('serverid', 'server_id'),
		('subitemid', 'subitem_id'),
		('inetmail', 'inet_mail'),
		('dotstuff', 'dot_stuff'),
		('newsfeed', 'news_feed'),
		('peruser', 'per_user'),
		('mailbeat', 'mail_beat'),
		('hotsite', 'hot_site'),
		('endtime', 'end_time'),
		('fixfont', 'fix_font'),
		('ccwrap', 'cc_wrap'),
		('metatag', 'meta_tag'),
		('iconurl', 'icon_url'),
		('itemproc', 'item_proc'),
		('viewinfo', 'view_info'),
		('displayname', 'display_name'),
		('fxsrcstream', 'fx_src_stream'),
		('fxdeststream', 'fx_dest_stream'),
		('othermailbox', 'other_mailbox'),
		('viewprivate', 'view_private'),
		('foldertype', 'folder_type'),
		('viewtype', 'view_type'),
		('ostid', 'ost_id'),
		('shareddata', 'shared_data'),
		('notfound', 'not_found'),
		('mapiuid', 'mapi_uid'),
		('mapiform', 'mapi_form'),
		('phonebook', 'phone_book'),
		('testclsid', 'test_clsid'),
		('labeleduri', 'labeled_uri'),
		('dispname', 'disp_name'),
		('syncevent', 'sync_event'),
		('slowlink', 'slow_link'),
		('dialup', 'dial_up'),
		('waitfor', 'wait_for'),
		('mimewrap', 'mime_wrap'),
		('tcpip', 'tcp_ip'),
		('traceinfo', 'trace_info'),
		('spamtype', 'spam_type'),
		('userfields', 'user_fields'),
		('viewlist', 'view_list'),
		('clearprops', 'clear_props'),
		('logfile', 'log_file'),
		('deltax', 'delta_x'),
		('deltay', 'delta_y'),
		('xpos', 'x_pos'),
		('ypos', 'y_pos'),
		('mailfrom', 'mail_from'),
		('datainit', 'data_init'),
		('dataterm', 'data_term'),
		('outq_', 'out_q_'),
		('inq_', 'in_q_'),
		('datablock', 'data_block'),
		('viewflags', 'view_flags'),
		('saveas', 'save_as'),
		('folderid', 'folder_id'),
		('portno', 'port_no'),
		('bifinfo', 'bif_info'),
		('msgtracking', 'msg_tracking'),
		('autoresponse', 'auto_response'),
		('favfld', 'fav_fld'),
		('bodypart', 'body_part'),
		('listinfo', 'list_info'),
		('reqcn', 'req_cn'),
		('reqname', 'req_name'),
		('insadmin', 'ins_admin')
	),
	OrigIdType.PID_TAG: (
		('_un_modified', '_unmodified'),
		('msgid', 'msg_id'),
		('itemid', 'item_id'),
		('replid', 'repl_id'),
		('guid', 'guid_'),
	),
	OrigIdType.PTAG: (
		("replid", "repl_id"),
	),
	None: (
		('temporaryflags', 'temporary_flags'),
		('errorinfo', 'error_info'),
		('msgsize', 'msg_size'),
		('attachlist', 'attach_list'),
		('changenum', 'change_num'),
		('addrbook', 'addr_book'),
		('rootdir', 'root_dir'),
		('msgclass', 'msg_class'),
		('messageclass', 'message_class'),
		('mtsid', 'mts_id'),
		('sentmail', 'sent_mail'),
		('to_do_', 'todo_'),
		('subfolder', 'sub_folder'),
		('rowid', 'row_id'),
		('recurrenceid', 'recurrence_id'),
		('readonly', 'read_only'),
		('pathname', 'path_name'),
		('templateid', 'template_id'),
		('datatype', 'data_type'),
		('codepage', 'code_page'),
		('_replid', '_repl_id'),
		('webviewinfo', 'webview_info'),
		('webview', 'web_view'),
		('mailuser', 'mail_user'),
		('longterm', 'long_term'),
		('newsfeed', 'news_feed')
	)
}

filters = {
	OrigIdType.PR_TAG: (
		('_oab_', '_offline_address_book_'),
		('ems_ab_', 'address_book_'),
		('_addr_', '_address_'),
		('_auth_', '_authorized_'),
		('_deliv_', '_delivery_'),
		('abeid', 'address_book_eid'),
		('_eid', '_entry_id'),
		('splus', 'schd_plus'),
		('_hab_', '_hier_'),
		('_dl', '_distr_list'),
		('_mhs_', '_message_handling_system_'),
		('_mta', '_message_transfer_agent'),
		('_reckey', '_record_key'),
		('wb_sf_', 'wb_search_folder_'),
		('_cont_', '_content_'),
		('_eid', '_entry_id'),
		('loglev', 'log_level'),
		('vrfy', 'verify'),
		('_hdrs_', '_headers_')
	),
	OrigIdType.PID_TAG: (
		('security_descriptor', 'nt_security_descriptor'),
		('_distribution_list', '_distr_list'),
		('_unauthorized_', '_unauth_'),
		('_away', 'oof'),
		('_t_bl_', '_table_')
	),
	None: (
		('appointment', 'appt'),
		('certificate', 'cert'),
		('recipient_', 'rcpt_'),
		('access_control_list_', 'acl_'),
		('hierarchical', 'hier'),
		('address', 'addr'),
		('message', 'msg'),
		('hasattach', 'has_attachments'),
		('_extended', '_ex'),
		('_eid', '_entry_id'),
		('_telephone_', '_phone_'),
		('received_', 'rcvd_'),
		('number', 'num'),
		('_object_', '_obj_'),
		('_message_', '_msg_'),
		('internet', 'inet'),
		('acct', 'account'),
		('maximum', 'max'),
		('minimum', 'min'),
		('transmitable', 'transmittable'),
		('_binary', '_bin'),
		('_mid_', '_msg_id_'),
		('_cpid', '_code_page_id'),
		('dam_', 'deferred_action_message_'),
		('attribute', 'attr'),
		('schedule_', 'schd_'),
	)
}


def processFilterBank(s, bank):
	for f in bank:
		s = s.replace(*f)
	return s


wordninjaFalsePositives = (
	"corre_lat_or",
	"e_its",
	"in_it",
	"i_pms",
	"rec_ip",
	"i_pm",
	"x_400",
	"x_500",
	"x_509",
	"x_25",
	"rfc_1006",
	"a_ddr",
	"re_pl",
	"rc_vd",
	"a_ppt",
	"tn_ef",
	"ds_a",
	"fr_eq",
	"a_lg",
	"auto_reply",
	"time_out",
	"a_ck",
	"re_cv",
	"rcp_t",
	"canonical_iz_ation",
	"map_i",
	"tn_s",
	"e_smtp",
	"e_trn",
	"s_mime",
	"synchronize_r",
	"rt_f",
	"acc_t",
	"gui_d",
	"mid_set",
	"x_mt",
	"sch_d",
	"spool_er",
	"nts_d",
	"n_td_n",
	"s_rc",
	"s_can",
	"de_st",
	"i_mail",
	"rm_q",
	"x_ref",
	"t_bl",
	"ow_a",
	"at_tr",
	"p_1",
	"u_id",
	"cl_sid",
	"out_box",
	"m_db",
	"as_soc",
	"p_2",
	"pre_c",
	"loop_back",
	"re_calc",
	"de_queue",
	"m_gr",
	"au_th",
	"start_tls",
	"ku_lane",
	"dia_g",
	"d_is_tr",
	"n_ntp",
	"if_s",
	"an_r",
	"c_dorm",
	"c_doo_or",
	"cd_of_bc",
	"s_vr",
	"transmit_able",
	"tty_tdd",
	"pa_b",
	"a_cl",
	"du_a",
	"ad_atp_3",
	"con_v",
	"p_km",
	"version_ing",
	"l_cid",
	"in_cr",
	"re_q",
	"rg_m",
	"c_pid",
	"fl_d",
	"ex_ch_50",
	"mb_in",
	"addr_s",
	"o_of",
	"sr_ch",
	"o_ab",
	"of_l",
	"open_ning",
	"encrypt_er",
	"fa_v",
	"m_sdos",
	"dx_a",
	"roll_over",
	"back_off",
	"de_sig",
	"una_u_th",
	"x_121",
	"xm_it",
	"l_dap",
	"cf_g",
	"adr_s",
	"mt_s",
	"pui_d",
	"mon_the_s",
	"x_view",
	"log_on",
	"cate_g",
	"back_fill",
	"in_st",
	"de_liv",
	"appt_s",
	"del_s",
	"reqc_n",
	"telet_ex"
)
wordninjaFalsePositives = [(el, el.replace("_", "")) for el in wordninjaFalsePositives]


def fix_after_wordninja(name):
	return attachNumber(processFilterBank(name, wordninjaFalsePositives))


def detectOrigIdTypeAndSplitFromRestOfName(name: str) -> OrigIdType:
	for k, v in origIdTypeToPrefixMapping.items():
		if k:
			if name.startswith(v):
				return k, name[len(v) :]
	
	return OrigIdType.unknown, name


def processFilterBundle(tp: OrigIdType, name: str, bundle, middleFixerFunc = None) -> str:
	filterBank = bundle.get(tp, ())
	name = processFilterBank(name, filterBank)

	if middleFixerFunc:
		name = middleFixerFunc(name)

	name = processFilterBank(name, bundle[None])

	return name


def splitJoinedWords(tp: OrigIdType, n: str, useWordNinja: bool = useWordNinja) -> str:
	"""Tries to normalize a name the way that different kinds of source names result into the same name. Also tries to make the name more easy to read"""

	#ic("splitJoinedWords", n)

	def middleFixerFunc(n: str) -> str:
		if useWordNinja:
			n = fix_after_wordninja("_".join(wnModel.split(n)))
			n = convertName(n, useWordNinja=False)
		return n
	
	n = processFilterBundle(tp, n, wordsSplitterFilters, middleFixerFunc)

	n = fixMultipleUnderscores(n)

	while n[-1] == "_":
		n = n[:-1]

	while n[0] == "_":
		n = n[1:]

	return n

from icecream import ic

typesConversionToUnderscoredRequired = frozenset((OrigIdType.PTAG, OrigIdType.PID_TAG, OrigIdType.INT_SCH_TAG))


def convertName(n: str, useWordNinja: bool = useWordNinja) -> str:
	"""Tries to normalize a name the way that different kinds of source names result into the same name. Also tries to make the name more easy to read"""

	tp, n = detectOrigIdTypeAndSplitFromRestOfName(n)
	#ic(tp, n)

	#if tp in typesConversionToUnderscoredRequired:
	if tp != OrigIdType.PR_TAG:  # typesConversionToUnderscoredRequired are all except OrigIdType.PR_TAG
		n = inflection.underscore(n)
		#ic("inflected", n)
	else:
		n = n.lower()

	def middleFixerFunc(n):
		#ic("After specific filter bundle", n)

		if tp == OrigIdType.PR_TAG:
			n = attachNumber(n)
		elif tp == OrigIdType.PTAG:
			n = n.replace("MTA", "MessageTransferAgent")

		n = n.lower()
		if "attachment" not in n:
			n.replace("has_attach", "has_attachments")

		n = splitJoinedWords(tp, n, useWordNinja=useWordNinja)
		return n

	n = processFilterBundle(tp, n, filters, middleFixerFunc)

	return n


def selectAndConvertNamesAdmissibleToId(origIds):
	for el in origIds:
		if allowedKSIdRx.match(el):
			yield convertName(el)


def prepareNamesAndOrigIds(origIds, sort: bool=True):
	origIds = list(dedupPreservingOrder(canonicalizeOrigName(el) for el in origIds))
	names = selectAndConvertNamesAdmissibleToId(origIds)
	if sort:
		names = sorted(set(names))
	else:
		names = dedupPreservingOrder(names)

	return origIds, names
