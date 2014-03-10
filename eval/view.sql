CREATE OR REPLACE VIEW occurences AS
SELECT
	v.variant AS variant,
	v.benchmark AS benchmark,
	p.data_address AS data_address,
	p.known_outcome AS known_outcome,
	p.data_width AS data_width,
	r.bitoffset AS bitoffset,
	r.resulttype AS resulttype,
	r.details AS details,
	r.original_value AS original_value,
	r.experiment_number AS experiment_number,
	f.path AS filename,
	s.linenumber AS linenumber,
	s.line AS source,
	p.injection_instr AS relative_instruction,
	p.injection_instr_absolute AS injection_instr,
	((t.time2 - t.time1 + 1) * width) AS occurrences
FROM variant v
JOIN trace t ON v.id = t.variant_id
JOIN fspgroup g ON g.variant_id = t.variant_id AND g.instr2 = t.instr2 AND g.data_address = t.data_address
JOIN result_CoredTesterProtoMsg r ON r.pilot_id = g.pilot_id
JOIN fsppilot p ON r.pilot_id = p.id
LEFT JOIN dbg_mapping m ON g.variant_id = m.variant_id AND p.injection_instr_absolute = m.instr_absolute
LEFT JOIN dbg_filename f ON m.variant_id = f.variant_id AND m.file_id = f.file_id
LEFT JOIN dbg_source s ON s.variant_id = m.variant_id AND s.linenumber = m.linenumber AND s.file_id = m.file_id
ORDER BY occurrences desc;
