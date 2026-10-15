FROM maven:3.9.11-eclipse-temurin-17 AS build
WORKDIR /src
COPY backend/pom.xml .
RUN mvn -B dependency:go-offline
COPY backend/src src
RUN mvn -B verify
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /src/target/control-plane-0.1.0.jar /app/app.jar
USER 10001
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
