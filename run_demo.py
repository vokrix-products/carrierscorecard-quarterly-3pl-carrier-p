from processor import process_file, reset_id_counter


DEMO_CSV = (
    "Carrier,Period,Segment,On Time Delivery %,On Time Pickup %,Tender Acceptance Rate,"
    "Claims Ratio,Invoice Accuracy %,Giveback %,Cost Variance %\n"
    "UPS,Q1 2025,Retail,96.4,95.1,97.3,0.32,98.1,-0.5,0.8\n"
    "U.P.S.,Q1 2025,Retail,91.2,90.4,88.0,0.72,94.0,-3.1,2.4\n"
    "FedEx,Q1 2025,Retail,88.5,89.0,80.1,1.4,89.2,-6.0,7.5\n"
    "United Parcel Service,Q1 2025,Industrial,93.0,92.5,90.5,0.6,93.5,-1.8,1.2\n"
    "DHL,Q1 2025,Healthcare,96.5,96.2,96.1,0.25,97.5,-0.9,0.4\n"
    "Unknown Logistics Co,Q1 2025,Retail,90.0,91.0,85.0,0.9,92.0,-4.0,3.0\n"
).encode("utf-8")


def main():
    reset_id_counter()
    result = process_file(DEMO_CSV)
    assert isinstance(result, list), "process_file must return a list"
    assert len(result) > 0, "process_file returned no records"
    for record in result:
        assert "title" in record, "record missing title"
        assert "status" in record, "record missing status"
        assert "details" in record, "record missing details"
        assert "due_date" in record, "record missing due_date"
    print(f"Processed {len(result)} carrier scorecard record(s).")
    for record in result:
        print(f"  [{record['status']:>7}] {record['title']}")
        print(f"           {record['details']}")
    return 0


if __name__ == "__main__":
    main()
